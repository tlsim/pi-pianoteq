from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.output import Output
from typing import Optional
import threading
import os

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.logging_config import BufferedLoggingHandler


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
        self.instrument_names = self.api.get_instrument_names()
        self.current_menu_index = 0
        self.menu_scroll_offset = 0
        self.menu_visible_items = 10

        # Set initial menu index to current instrument
        current_instrument = self.api.get_current_instrument()
        try:
            self.current_menu_index = self.instrument_names.index(current_instrument)
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
            if self.menu_mode:
                # Exit menu mode
                self.menu_mode = False
                self._update_display()
            else:
                # Exit application
                event.app.exit()

        @kb.add('escape')
        def kb_escape(event):
            if self.menu_mode:
                self.menu_mode = False
                self._update_display()

        # Normal mode: Arrow keys for navigation
        @kb.add('up')
        @kb.add('c-p')
        def kb_up(event):
            if self.menu_mode:
                self._menu_prev()
            else:
                self.api.set_preset_prev()
            self._update_display()

        @kb.add('down')
        @kb.add('c-n')
        def kb_down(event):
            if self.menu_mode:
                self._menu_next()
            else:
                self.api.set_preset_next()
            self._update_display()

        @kb.add('left')
        @kb.add('c-b')
        def kb_left(event):
            if not self.menu_mode:
                self.api.set_instrument_prev()
                self._update_display()

        @kb.add('right')
        @kb.add('c-f')
        def kb_right(event):
            if not self.menu_mode:
                self.api.set_instrument_next()
                self._update_display()

        # Enter instrument menu
        @kb.add('i')
        @kb.add('c-i')
        def kb_menu(event):
            if not self.menu_mode:
                self.menu_mode = True
                # Set menu index to current instrument
                current_instrument = self.api.get_current_instrument()
                try:
                    self.current_menu_index = self.instrument_names.index(current_instrument)
                    self._update_scroll_offset()
                except ValueError:
                    pass
                self._update_display()

        # Select instrument in menu mode
        @kb.add('enter')
        def kb_select(event):
            if self.menu_mode:
                selected_instrument = self.instrument_names[self.current_menu_index]
                self.api.set_instrument(selected_instrument)
                self.menu_mode = False
                self._update_display()

        return kb

    def show_loading_message(self, message: str):
        """Update loading message and trigger redraw"""
        self.loading_message = message

        # Start app in background thread if not already running
        if not self.app_running:
            self.app_running = True
            self.app_thread = threading.Thread(target=self.application.run, daemon=True)
            self.app_thread.start()

        # Trigger redraw
        self.application.invalidate()

    def _menu_next(self):
        """Navigate to next menu item"""
        if self.current_menu_index < len(self.instrument_names) - 1:
            self.current_menu_index += 1
            self._update_scroll_offset()

    def _menu_prev(self):
        """Navigate to previous menu item"""
        if self.current_menu_index > 0:
            self.current_menu_index -= 1
            self._update_scroll_offset()

    def _update_scroll_offset(self):
        """Update scroll offset to keep selected item visible"""
        # Keep selected item in the middle of the visible area when possible
        mid_point = self.menu_visible_items // 2

        if self.current_menu_index < mid_point:
            # Near the top
            self.menu_scroll_offset = 0
        elif self.current_menu_index >= len(self.instrument_names) - mid_point:
            # Near the bottom
            self.menu_scroll_offset = max(0, len(self.instrument_names) - self.menu_visible_items)
        else:
            # Middle - center the selection
            self.menu_scroll_offset = self.current_menu_index - mid_point

    def _get_title(self):
        """Get frame title based on current mode"""
        if self.menu_mode:
            return "Select Instrument"
        else:
            return "Pi-Pianoteq CLI"

    def _get_display_text(self):
        """Generate display text based on current mode"""
        if self.menu_mode:
            return self._get_menu_text()
        else:
            return self._get_normal_text()

    def _get_normal_text(self):
        """Generate normal mode display using formatted text tuples"""
        instrument = self.api.get_current_instrument()
        preset = self.api.get_current_preset_display_name()

        # Use list of (style, text) tuples for proper formatting
        lines = [
            ('', '\n'),
            ('bold cyan', 'Instrument:'), ('', '\n'),
            ('ansigreen', f'  {instrument}'), ('', '\n'),
            ('', '\n'),
            ('bold cyan', 'Preset:'), ('', '\n'),
            ('ansiyellow', f'  {preset}'), ('', '\n'),
            ('', '\n'),
            ('bold underline', 'Controls:'), ('', '\n'),
            ('', '  Up/Down     : Navigate presets\n'),
            ('', '  Left/Right  : Quick instrument switch\n'),
            ('bold', '  i'), ('', '           : Open instrument menu\n'),
            ('bold', '  q'), ('', '           : Quit\n'),
            ('', '\n'),
        ]

        return lines

    def _get_menu_text(self):
        """Generate menu mode display using formatted text tuples"""
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
            ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Exit menu\n'),
            ('', '\n'),
        ])

        return lines

    def _update_display(self):
        """Force display refresh"""
        self.application.invalidate()

    def start(self):
        """Start or join the application"""
        if self.app_running:
            # App already running in background thread, just wait for it
            if self.app_thread:
                self.app_thread.join()
        else:
            # Start app normally (blocking)
            self.application.run()
