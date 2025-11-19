from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.filters import Condition
from typing import Optional
import threading
import os

from pi_pianoteq.client.client import Client
from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.cli.search_manager import SearchManager
from pi_pianoteq.client.cli import cli_display
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
        return cli_display.format_log_messages(self.log_buffer, reserved_lines=12, default_max_lines=20)

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
        self.preset_menu_instrument = None
        self.logs_view_mode = False
        self.instrument_names = [i.name for i in self.api.get_instruments()]
        self.preset_names = []
        self.current_menu_index = 0
        self.menu_scroll_offset = 0

        # Search manager
        self.search_manager = SearchManager(self.api)

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
            if self.search_manager.is_active():
                # Exit search mode
                self.search_manager.exit_search()
                self.current_menu_index = 0
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
            elif self.logs_view_mode:
                # Exit logs view mode
                self.logs_view_mode = False
                self._update_display()
            else:
                # Exit application
                event.app.exit()

        @kb.add('escape')
        def kb_escape(event):
            if self.search_manager.is_active():
                self.search_manager.exit_search()
                self.current_menu_index = 0
                self._update_display()
            elif self.preset_menu_mode:
                self.preset_menu_mode = False
                self.preset_menu_instrument = None
                self._update_display()
            elif self.menu_mode:
                self.menu_mode = False
                self._update_display()
            elif self.logs_view_mode:
                self.logs_view_mode = False
                self._update_display()

        # Normal mode: Arrow keys for navigation
        @kb.add('up')
        @kb.add('c-p')
        def kb_up(event):
            if self.search_manager.is_active() or self.preset_menu_mode or self.menu_mode:
                self._menu_prev()
            else:
                self.api.set_preset_prev()
            self._update_display()

        @kb.add('down')
        @kb.add('c-n')
        def kb_down(event):
            if self.search_manager.is_active() or self.preset_menu_mode or self.menu_mode:
                self._menu_next()
            else:
                self.api.set_preset_next()
            self._update_display()

        @kb.add('left')
        @kb.add('c-b')
        def kb_left(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active():
                self.api.set_instrument_prev()
                self._update_display()

        @kb.add('right')
        @kb.add('c-f')
        def kb_right(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active():
                self.api.set_instrument_next()
                self._update_display()

        # Enter instrument menu
        @kb.add('i')
        def kb_menu(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active():
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
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active():
                # Open preset menu for current instrument
                current_instrument = self.api.get_current_instrument()
                self._open_preset_menu(current_instrument.name)
            elif self.menu_mode and not self.search_manager.is_active():
                # Open preset menu for selected instrument in instrument menu
                selected_instrument = self.instrument_names[self.current_menu_index]
                self._open_preset_menu(selected_instrument)

        # Enter search mode
        @kb.add('/')
        def kb_search(event):
            if not self.search_manager.is_active():
                if self.preset_menu_mode:
                    self.search_manager.enter_search('preset', self.preset_menu_instrument)
                elif self.menu_mode:
                    self.search_manager.enter_search('instrument')
                else:
                    self.search_manager.enter_search('combined')
                self.current_menu_index = 0
                self._update_display()

        # Enter logs view mode
        @kb.add('l')
        def kb_logs(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active() and not self.logs_view_mode:
                self.logs_view_mode = True
                self._update_display()

        # Randomize current preset
        @kb.add('r')
        def kb_randomize_preset(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active() and not self.logs_view_mode:
                self.api.randomize_current_preset()
                self._update_display()

        # Random instrument and randomize parameters
        @kb.add('R')
        def kb_random_instrument(event):
            if not self.menu_mode and not self.preset_menu_mode and not self.search_manager.is_active() and not self.logs_view_mode:
                self.api.randomize_instrument_and_preset()
                self._update_display()

        # Handle text input in search mode
        for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.,()[]':
            @kb.add(char, filter=Condition(lambda: self.search_manager.is_active()))
            def kb_char(event, c=char):
                self.search_manager.set_query(self.search_manager.query + c)
                self.current_menu_index = 0
                self._update_scroll_offset()
                self._update_display()

        # Backspace in search mode
        @kb.add('backspace')
        def kb_backspace(event):
            if self.search_manager.is_active() and self.search_manager.query:
                self.search_manager.set_query(self.search_manager.query[:-1])
                self.current_menu_index = 0
                self._update_scroll_offset()
                self._update_display()
            elif self.search_manager.is_active() and not self.search_manager.query:
                # Exit search mode if query is empty
                self.search_manager.exit_search()
                self.current_menu_index = 0
                self._update_scroll_offset()
                self._update_display()

        # Select instrument/preset in menu mode
        @kb.add('enter')
        def kb_select(event):
            if self.search_manager.is_active():
                # Select from search results
                action = self.search_manager.get_selection_action(self.current_menu_index)
                if action:
                    action_type, action_data = action
                    if action_type == 'set_instrument':
                        self.api.set_instrument(action_data)
                    elif action_type == 'set_preset':
                        instrument_name, preset_name = action_data
                        self.api.set_preset(instrument_name, preset_name)
                    elif action_type == 'set_preset_single':
                        self.api.set_preset(self.search_manager.preset_menu_instrument, action_data)

                    # Exit all menus
                    self.search_manager.exit_search()
                    self.preset_menu_mode = False
                    self.menu_mode = False
                    self.current_menu_index = 0
                    self._update_display()
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

    def _menu_next(self):
        """Navigate to next menu item"""
        if self.search_manager.is_active():
            menu_items = self.search_manager.filtered_items
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
        if self.search_manager.is_active():
            menu_items = self.search_manager.filtered_items
        elif self.preset_menu_mode:
            menu_items = self.preset_names
        else:
            menu_items = self.instrument_names

        # Calculate visible items based on current terminal size
        menu_visible_items = cli_display.calculate_menu_visible_items()

        # Keep selected item in the middle of the visible area when possible
        mid_point = menu_visible_items // 2

        if self.current_menu_index < mid_point:
            # Near the top
            self.menu_scroll_offset = 0
        elif self.current_menu_index >= len(menu_items) - mid_point:
            # Near the bottom
            self.menu_scroll_offset = max(0, len(menu_items) - menu_visible_items)
        else:
            # Middle - center the selection
            self.menu_scroll_offset = self.current_menu_index - mid_point

    def _get_title(self):
        """Get frame title based on current mode"""
        return cli_display.get_title(
            self.search_manager,
            self.preset_menu_mode,
            self.preset_menu_instrument,
            self.menu_mode,
            self.logs_view_mode
        )

    def _get_display_text(self):
        """Generate display text based on current mode"""
        if self.logs_view_mode:
            return cli_display.get_logs_view_text(self.log_buffer)
        elif self.search_manager.is_active():
            return cli_display.get_search_text(
                self.search_manager,
                self.current_menu_index,
                self.menu_scroll_offset
            )
        elif self.preset_menu_mode:
            return cli_display.get_preset_menu_text(
                self.api,
                self.preset_menu_instrument,
                self.current_menu_index,
                self.menu_scroll_offset
            )
        elif self.menu_mode:
            return cli_display.get_instrument_menu_text(
                self.instrument_names,
                self.current_menu_index,
                self.menu_scroll_offset
            )
        else:
            return cli_display.get_normal_text(self.api)

    def _update_display(self):
        """Force display refresh"""
        self.application.invalidate()

    def start(self):
        """Wait for the application to exit"""
        # App is already running in background thread, just wait for it
        if self.app_thread:
            self.app_thread.join()
