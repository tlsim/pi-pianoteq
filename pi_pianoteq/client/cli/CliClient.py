from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from typing import Optional

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class CliClient(Client):
    """
    CLI client for Pianoteq with instrument selection menu and arrow key navigation.

    Loading mode (api=None): Simple console output for loading messages
    Normal mode (after set_api): Full interactive CLI

    Modes during normal operation:
    - Normal mode: Display current instrument/preset, navigate with arrows
    - Menu mode: Select instruments from a scrollable list
    """

    def __init__(self, api: Optional[ClientApi]):
        super().__init__(api)

        # Loading mode state
        self.loading_mode = (api is None)
        self.application = None

        # Initialize interactive CLI if API provided
        if api is not None:
            self._init_interactive_cli()

    def _init_interactive_cli(self):
        """Initialize the interactive CLI (requires API)"""
        # State management
        self.menu_mode = False
        self.instrument_names = self.api.get_instrument_names()
        self.current_menu_index = 0
        self.menu_scroll_offset = 0
        self.menu_visible_items = 10  # Number of menu items to show at once

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
        layout = Layout(container=root_container)

        # Key bindings
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

        # Build main application
        self.application = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True
        )
        self.loading_mode = False

    def set_api(self, api: ClientApi):
        """Provide API and initialize interactive CLI"""
        self.api = api
        self._init_interactive_cli()

    def show_loading_message(self, message: str):
        """Display a loading message (simple console print in CLI mode)"""
        print(f"  {message}")

    def clear_loading_screen(self):
        """Clear loading screen (just print a separator)"""
        print()

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
        """Start the interactive CLI application (requires API)"""
        if self.loading_mode:
            raise RuntimeError("Cannot start client in loading mode. Call set_api() first.")
        self.application.run()
