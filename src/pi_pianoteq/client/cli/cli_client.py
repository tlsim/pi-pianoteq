from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.widgets import Frame, SearchToolbar
from prompt_toolkit.output import Output
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import Condition
from typing import Optional, List, Tuple
import threading
import os

from pi_pianoteq.client.client import Client
from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.logging.logging_config import BufferedLoggingHandler


class CliClient(Client):
    """
    CLI client for Pianoteq with instrument selection menu and arrow key navigation.

    Loading mode (api=None): Full-screen loading display
    Normal mode (after set_api): Full interactive CLI with instrument/preset display

    Modes during normal operation:
    - Normal mode: Display current instrument/preset, navigate with arrows
    - Menu mode: Select instruments from a scrollable list
    """

    def __init__(self, api: Optional[ClientApi]):
        super().__init__(api)

        # Loading mode state
        self.loading_mode = (api is None)
        self.loading_message = "Initializing..."
        self.app_thread = None
        self.app_running = False

        # Create log buffer for displaying logs in UI
        self.log_buffer = BufferedLoggingHandler(maxlen=50)

        # Initialize application (should always start with loading mode now)
        if api is None:
            self._init_loading_app()
            # Start application in background thread immediately
            self.app_running = True
            self.app_thread = threading.Thread(target=self.application.run, daemon=True)
            self.app_thread.start()
        else:
            # Shouldn't reach here in normal flow, but handle gracefully
            raise RuntimeError("CliClient should be initialized with api=None for loading mode")

    def _init_loading_app(self):
        """Initialize the loading screen Application"""
        # Create loading message control
        self.loading_control = FormattedTextControl(
            text=self._get_loading_text,
            focusable=False
        )

        # Create log display control
        self.log_control = FormattedTextControl(
            text=self._get_log_text,
            focusable=False
        )

        # Create layout with message at top and logs below
        loading_message_window = Window(content=self.loading_control, height=6)
        log_window = Window(
            content=self.log_control,
            wrap_lines=False,
            always_hide_cursor=True,
            scroll_offsets=None  # Allow natural scrolling to bottom
        )

        content = HSplit([
            loading_message_window,
            log_window,
        ])

        loading_container = Frame(content, title="Pi-Pianoteq")
        loading_layout = Layout(container=loading_container)

        # Simple key bindings for loading mode (just Ctrl-C to exit)
        loading_kb = KeyBindings()

        @loading_kb.add('c-c')
        def kb_exit(event):
            event.app.exit()

        # Create application
        self.application = Application(
            layout=loading_layout,
            key_bindings=loading_kb,
            full_screen=True
        )

        # Set callback to update UI when new log messages arrive
        self.log_buffer.set_callback(self.application.invalidate)

    def _get_loading_text(self):
        """Generate loading text display"""
        return [
            ('', '\n'),
            ('bold cyan', '  Loading Pi-Pianoteq\n'),
            ('', '\n'),
            ('', f'  {self.loading_message}\n'),
        ]

    def _get_log_text(self):
        """Generate log text display from buffered messages"""
        messages = self.log_buffer.get_messages()
        if not messages:
            return [('ansigray', '  Initializing...\n')]

        # Calculate how many lines can fit on screen
        # Terminal height minus loading message area (6 lines) minus frame (3 lines) minus padding
        try:
            terminal_height = os.get_terminal_size().lines
            max_log_lines = max(10, terminal_height - 12)  # At least 10, otherwise height - 12
        except (OSError, AttributeError):
            max_log_lines = 20  # Default if can't detect terminal size

        # Return last N messages that fit
        lines = []
        visible_messages = messages[-max_log_lines:]
        for msg in visible_messages:
            lines.append(('ansibrightblack', f'  {msg}\n'))
        return lines

    def set_api(self, api: ClientApi):
        """Provide API and switch to normal layout"""
        self.api = api
        self.loading_mode = False

        # Build normal layout
        self._build_normal_layout()

        # Switch to normal layout
        self.application.layout = self.normal_layout
        self.application.key_bindings = self.normal_kb

        # Trigger redraw
        self.application.invalidate()

    def _build_normal_layout(self):
        """Build the normal interactive layout (requires API)"""
        # State management
        self.menu_mode = False
        self.preset_menu_mode = False
        self.search_mode = False
        self.preset_menu_instrument = None
        self.instrument_names = [i.name for i in self.api.get_instruments()]
        self.preset_names = []
        self.current_menu_index = 0
        self.menu_scroll_offset = 0
        self.menu_visible_items = 10
        self.search_query = ""
        self.filtered_items = []
        self.search_context = None

        # Set initial menu index to current instrument
        current_instrument = self.api.get_current_instrument()
        try:
            self.current_menu_index = self.instrument_names.index(current_instrument.name)
        except ValueError:
            self.current_menu_index = 0

        # Create display controls
        self.display_control = FormattedTextControl(
            text=self._get_display_text,
            focusable=False
        )

        # Create layout with frame
        content_window = Window(content=self.display_control)
        root_container = Frame(content_window, title=self._get_title)
        self.normal_layout = Layout(container=root_container)

        # Key bindings for normal mode
        self.normal_kb = self._build_normal_keybindings()

    def _build_normal_keybindings(self):
        """Build key bindings for normal operation"""
        kb = KeyBindings()

        # Exit bindings
        @kb.add('c-c')
        @kb.add('q')
        def kb_exit(event):
            if self.search_mode:
                # Exit search mode
                self._exit_search_mode()
                self._update_display()
            elif self.preset_menu_mode:
                # Exit preset menu mode
                self.preset_menu_mode = False
                self.preset_menu_instrument = None
                self._update_display()
            elif self.menu_mode:
                # Exit menu mode
                self.menu_mode = False
                self._update_display()
            else:
                # Exit application
                event.app.exit()

        @kb.add('escape')
        def kb_escape(event):
            if self.search_mode:
                self._exit_search_mode()
                self._update_display()
            elif self.preset_menu_mode:
                self.preset_menu_mode = False
                self.preset_menu_instrument = None
                self._update_display()
            elif self.menu_mode:
                self.menu_mode = False
                self._update_display()

        # Normal mode: Arrow keys for navigation
        @kb.add('up')
        @kb.add('c-p')
        def kb_up(event):
            if self.search_mode or self.preset_menu_mode or self.menu_mode:
                self._menu_prev()
            else:
                self.api.set_preset_prev()
            self._update_display()

        @kb.add('down')
        @kb.add('c-n')
        def kb_down(event):
            if self.search_mode or self.preset_menu_mode or self.menu_mode:
                self._menu_next()
            else:
                self.api.set_preset_next()
            self._update_display()

        @kb.add('left')
        @kb.add('c-b')
        def kb_left(event):
            if not self.menu_mode and not self.preset_menu_mode:
                self.api.set_instrument_prev()
                self._update_display()

        @kb.add('right')
        @kb.add('c-f')
        def kb_right(event):
            if not self.menu_mode and not self.preset_menu_mode:
                self.api.set_instrument_next()
                self._update_display()

        # Enter instrument menu
        @kb.add('i')
        def kb_menu(event):
            if not self.menu_mode and not self.preset_menu_mode:
                self.menu_mode = True
                # Set menu index to current instrument
                current_instrument = self.api.get_current_instrument()
                try:
                    self.current_menu_index = self.instrument_names.index(current_instrument.name)
                    self._update_scroll_offset()
                except ValueError:
                    pass
                self._update_display()

        # Enter preset menu for current instrument
        @kb.add('p')
        def kb_preset_menu(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_mode:
                # Open preset menu for current instrument
                current_instrument = self.api.get_current_instrument()
                self._open_preset_menu(current_instrument.name)
            elif self.menu_mode and not self.search_mode:
                # Open preset menu for selected instrument in instrument menu
                selected_instrument = self.instrument_names[self.current_menu_index]
                self._open_preset_menu(selected_instrument)

        # Enter search mode
        @kb.add('/')
        def kb_search(event):
            if not self.search_mode:
                if self.preset_menu_mode:
                    self._enter_search_mode('preset')
                elif self.menu_mode:
                    self._enter_search_mode('instrument')
                else:
                    self._enter_search_mode('combined')

        # Handle text input in search mode
        for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.,()[]':
            @kb.add(char)
            def kb_char(event, c=char):
                if self.search_mode:
                    self.search_query += c
                    self._update_search_results()
                    self._update_display()

        # Backspace in search mode
        @kb.add('backspace')
        def kb_backspace(event):
            if self.search_mode and self.search_query:
                self.search_query = self.search_query[:-1]
                self._update_search_results()
                self._update_display()
            elif self.search_mode and not self.search_query:
                # Exit search mode if query is empty
                self._exit_search_mode()
                self._update_display()

        # Select instrument/preset in menu mode
        @kb.add('enter')
        def kb_select(event):
            if self.search_mode:
                # Select from search results
                self._select_search_result()
            elif self.preset_menu_mode:
                # Select preset from preset menu
                preset_name = self.preset_names[self.current_menu_index]
                self.api.set_preset(self.preset_menu_instrument, preset_name)
                self.preset_menu_mode = False
                self.preset_menu_instrument = None
                # Also exit instrument menu if open
                if self.menu_mode:
                    self.menu_mode = False
                self._update_display()
            elif self.menu_mode:
                # Select instrument from instrument menu
                selected_instrument = self.instrument_names[self.current_menu_index]
                self.api.set_instrument(selected_instrument)
                self.menu_mode = False
                self._update_display()

        return kb

    def show_loading_message(self, message: str):
        """Update loading message and trigger redraw"""
        self.loading_message = message
        self.application.invalidate()

    def _open_preset_menu(self, instrument_name: str):
        """Open preset menu for specified instrument"""
        self.preset_menu_mode = True
        self.preset_menu_instrument = instrument_name

        # Get presets for the instrument (display names)
        presets = self.api.get_presets(instrument_name)
        self.preset_names = [p.name for p in presets]

        # Set initial selection to current preset if viewing current instrument
        if instrument_name == self.api.get_current_instrument().name:
            current_preset = self.api.get_current_preset()
            try:
                self.current_menu_index = self.preset_names.index(current_preset.name)
            except ValueError:
                self.current_menu_index = 0
        else:
            self.current_menu_index = 0

        self._update_scroll_offset()
        self._update_display()

    def _enter_search_mode(self, context: str):
        """Enter search mode with given context (instrument/preset/combined)"""
        self.search_mode = True
        self.search_context = context
        self.search_query = ""
        self.filtered_items = []
        self.current_menu_index = 0
        self._update_search_results()
        self._update_display()

    def _exit_search_mode(self):
        """Exit search mode and restore previous state"""
        self.search_mode = False
        self.search_query = ""
        self.filtered_items = []
        self.search_context = None
        self.current_menu_index = 0

    def _update_search_results(self):
        """Update filtered items based on current search query"""
        query = self.search_query.lower()

        if self.search_context == 'instrument':
            # Search instruments only
            all_items = [(name, 'instrument', name) for name in self.instrument_names]
        elif self.search_context == 'preset':
            # Search presets only (for current preset menu instrument)
            presets = self.api.get_presets(self.preset_menu_instrument)
            all_items = [(p.display_name, 'preset', p.name) for p in presets]
        else:  # combined
            # Search both instruments and presets
            all_items = []
            # Add instruments
            for name in self.instrument_names:
                all_items.append((name, 'instrument', name))
            # Add presets from all instruments
            for instrument in self.api.get_instruments():
                for preset in instrument.presets:
                    all_items.append((f"{preset.display_name} ({instrument.name})", 'preset', (instrument.name, preset.name)))

        # Filter items by query
        if query:
            self.filtered_items = [
                item for item in all_items
                if query in item[0].lower()
            ]
        else:
            self.filtered_items = all_items

        # Reset selection to first item
        if self.filtered_items:
            self.current_menu_index = 0
        self._update_scroll_offset()

    def _select_search_result(self):
        """Select the currently highlighted search result"""
        if not self.filtered_items or self.current_menu_index >= len(self.filtered_items):
            return

        display_name, item_type, data = self.filtered_items[self.current_menu_index]

        if item_type == 'instrument':
            # Select instrument
            self.api.set_instrument(data)
            # Exit all menus
            self.search_mode = False
            self.preset_menu_mode = False
            self.menu_mode = False
        else:  # preset
            if self.search_context == 'combined':
                # Combined search: data is (instrument_name, preset_name)
                instrument_name, preset_name = data
                self.api.set_preset(instrument_name, preset_name)
            else:
                # Preset-only search: data is just preset_name
                preset_name = data
                self.api.set_preset(self.preset_menu_instrument, preset_name)
            # Exit all menus
            self.search_mode = False
            self.preset_menu_mode = False
            self.menu_mode = False

        self._update_display()

    def _menu_next(self):
        """Navigate to next menu item"""
        if self.search_mode:
            menu_items = self.filtered_items
        elif self.preset_menu_mode:
            menu_items = self.preset_names
        else:
            menu_items = self.instrument_names

        if self.current_menu_index < len(menu_items) - 1:
            self.current_menu_index += 1
            self._update_scroll_offset()

    def _menu_prev(self):
        """Navigate to previous menu item"""
        if self.current_menu_index > 0:
            self.current_menu_index -= 1
            self._update_scroll_offset()

    def _update_scroll_offset(self):
        """Update scroll offset to keep selected item visible"""
        # Get current menu items
        if self.search_mode:
            menu_items = self.filtered_items
        elif self.preset_menu_mode:
            menu_items = self.preset_names
        else:
            menu_items = self.instrument_names

        # Keep selected item in the middle of the visible area when possible
        mid_point = self.menu_visible_items // 2

        if self.current_menu_index < mid_point:
            # Near the top
            self.menu_scroll_offset = 0
        elif self.current_menu_index >= len(menu_items) - mid_point:
            # Near the bottom
            self.menu_scroll_offset = max(0, len(menu_items) - self.menu_visible_items)
        else:
            # Middle - center the selection
            self.menu_scroll_offset = self.current_menu_index - mid_point

    def _get_title(self):
        """Get frame title based on current mode"""
        if self.search_mode:
            if self.search_context == 'instrument':
                return "Search Instruments"
            elif self.search_context == 'preset':
                return f"Search Presets - {self.preset_menu_instrument}"
            else:
                return "Search Instruments & Presets"
        elif self.preset_menu_mode:
            return f"Select Preset - {self.preset_menu_instrument}"
        elif self.menu_mode:
            return "Select Instrument"
        else:
            return "Pi-Pianoteq CLI"

    def _get_display_text(self):
        """Generate display text based on current mode"""
        if self.search_mode:
            return self._get_search_text()
        elif self.preset_menu_mode:
            return self._get_preset_menu_text()
        elif self.menu_mode:
            return self._get_instrument_menu_text()
        else:
            return self._get_normal_text()

    def _get_normal_text(self):
        """Generate normal mode display using formatted text tuples"""
        instrument = self.api.get_current_instrument()
        preset = self.api.get_current_preset().display_name

        # Use list of (style, text) tuples for proper formatting
        lines = [
            ('', '\n'),
            ('bold cyan', 'Instrument:'), ('', '\n'),
            ('ansigreen', f'  {instrument.name}'), ('', '\n'),
            ('', '\n'),
            ('bold cyan', 'Preset:'), ('', '\n'),
            ('ansiyellow', f'  {preset}'), ('', '\n'),
            ('', '\n'),
            ('bold underline', 'Controls:'), ('', '\n'),
            ('', '  Up/Down     : Navigate presets\n'),
            ('', '  Left/Right  : Quick instrument switch\n'),
            ('bold', '  i'), ('', '           : Open instrument menu\n'),
            ('bold', '  p'), ('', '           : Open preset menu\n'),
            ('bold', '  /'), ('', '           : Search instruments & presets\n'),
            ('bold', '  q'), ('', '           : Quit\n'),
            ('', '\n'),
        ]

        return lines

    def _get_instrument_menu_text(self):
        """Generate instrument menu display using formatted text tuples"""
        lines = [('', '\n')]

        # Calculate visible range
        start_idx = self.menu_scroll_offset
        end_idx = min(start_idx + self.menu_visible_items, len(self.instrument_names))

        # Add scroll indicator if needed
        if start_idx > 0:
            lines.append(('ansigray', '  ... (Up for more)\n'))
        else:
            lines.append(('', '\n'))

        # Add visible menu items
        for i in range(start_idx, end_idx):
            instrument = self.instrument_names[i]
            # Truncate long names to fit in display
            display_name = instrument[:58] if len(instrument) > 58 else instrument

            if i == self.current_menu_index:
                # Highlight selected item
                lines.append(('bold cyan', f'  > {display_name}\n'))
            else:
                lines.append(('', f'    {display_name}\n'))

        # Fill remaining space if needed
        displayed_items = end_idx - start_idx
        if start_idx > 0:
            displayed_items += 1  # Account for "..." line

        for _ in range(self.menu_visible_items - displayed_items):
            lines.append(('', '\n'))

        # Add scroll indicator at bottom if needed
        if end_idx < len(self.instrument_names):
            lines.append(('ansigray', '  ... (Down for more)\n'))
        else:
            lines.append(('', '\n'))

        lines.extend([
            ('', '\n'),
            ('bold underline', 'Menu Controls:'), ('', '\n'),
            ('', '  Up/Down  : Navigate menu\n'),
            ('bold', '  Enter'), ('', '    : Select instrument\n'),
            ('bold', '  p'), ('', '        : View presets for selected instrument\n'),
            ('bold', '  /'), ('', '        : Search instruments\n'),
            ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Exit menu\n'),
            ('', '\n'),
        ])

        return lines

    def _get_preset_menu_text(self):
        """Generate preset menu display using formatted text tuples"""
        lines = [('', '\n')]

        # Get presets with display names
        presets = self.api.get_presets(self.preset_menu_instrument)

        # Calculate visible range
        start_idx = self.menu_scroll_offset
        end_idx = min(start_idx + self.menu_visible_items, len(presets))

        # Add scroll indicator if needed
        if start_idx > 0:
            lines.append(('ansigray', '  ... (Up for more)\n'))
        else:
            lines.append(('', '\n'))

        # Add visible menu items
        for i in range(start_idx, end_idx):
            preset = presets[i]
            # Truncate long names to fit in display
            display_name = preset.display_name[:58] if len(preset.display_name) > 58 else preset.display_name

            if i == self.current_menu_index:
                # Highlight selected item
                lines.append(('bold cyan', f'  > {display_name}\n'))
            else:
                lines.append(('', f'    {display_name}\n'))

        # Fill remaining space if needed
        displayed_items = end_idx - start_idx
        if start_idx > 0:
            displayed_items += 1  # Account for "..." line

        for _ in range(self.menu_visible_items - displayed_items):
            lines.append(('', '\n'))

        # Add scroll indicator at bottom if needed
        if end_idx < len(presets):
            lines.append(('ansigray', '  ... (Down for more)\n'))
        else:
            lines.append(('', '\n'))

        lines.extend([
            ('', '\n'),
            ('bold underline', 'Menu Controls:'), ('', '\n'),
            ('', '  Up/Down  : Navigate menu\n'),
            ('bold', '  Enter'), ('', '    : Select preset\n'),
            ('bold', '  /'), ('', '        : Search presets\n'),
            ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Exit menu\n'),
            ('', '\n'),
        ])

        return lines

    def _get_search_text(self):
        """Generate search mode display using formatted text tuples"""
        lines = [('', '\n')]

        # Show search query
        lines.extend([
            ('bold cyan', 'Search: '), ('ansiyellow', self.search_query), ('', '\n'),
            ('', '\n'),
        ])

        # Show result count
        result_count = len(self.filtered_items)
        if result_count == 0:
            lines.append(('ansigray', f'  No matches found\n'))
            lines.append(('', '\n'))
        else:
            lines.append(('ansigray', f'  {result_count} result(s)\n'))

        # Calculate visible range
        start_idx = self.menu_scroll_offset
        end_idx = min(start_idx + self.menu_visible_items, len(self.filtered_items))

        # Add scroll indicator if needed
        if start_idx > 0:
            lines.append(('ansigray', '  ... (Up for more)\n'))
        else:
            lines.append(('', '\n'))

        # Add visible search results
        for i in range(start_idx, end_idx):
            display_name, item_type, data = self.filtered_items[i]
            # Truncate long names to fit in display
            display_text = display_name[:56] if len(display_name) > 56 else display_name

            # Add type indicator
            if self.search_context == 'combined':
                type_indicator = '[I]' if item_type == 'instrument' else '[P]'
                display_text = f"{type_indicator} {display_text}"

            if i == self.current_menu_index:
                # Highlight selected item
                lines.append(('bold cyan', f'  > {display_text}\n'))
            else:
                lines.append(('', f'    {display_text}\n'))

        # Fill remaining space if needed
        displayed_items = end_idx - start_idx
        if start_idx > 0:
            displayed_items += 1  # Account for "..." line

        for _ in range(self.menu_visible_items - displayed_items):
            lines.append(('', '\n'))

        # Add scroll indicator at bottom if needed
        if end_idx < len(self.filtered_items):
            lines.append(('ansigray', '  ... (Down for more)\n'))
        else:
            lines.append(('', '\n'))

        lines.extend([
            ('', '\n'),
            ('bold underline', 'Search Controls:'), ('', '\n'),
            ('', '  Type to search\n'),
            ('', '  Up/Down     : Navigate results\n'),
            ('bold', '  Enter'), ('', '       : Select item\n'),
            ('bold', '  Backspace'), ('', '   : Delete character (or exit if empty)\n'),
            ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', '    : Exit search\n'),
            ('', '\n'),
        ])

        return lines

    def _update_display(self):
        """Force display refresh"""
        self.application.invalidate()

    def start(self):
        """Wait for the application to exit"""
        # App is already running in background thread, just wait for it
        if self.app_thread:
            self.app_thread.join()
