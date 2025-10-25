from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class CliClient(Client):
    """
    CLI client for Pianoteq with instrument selection menu and arrow key navigation.

    Modes:
    - Normal mode: Display current instrument/preset, navigate with arrows
    - Menu mode: Select instruments from a scrollable list
    """

    def __init__(self, api: ClientApi):
        super().__init__(api)

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

        # Create layout
        root_container = HSplit([
            Window(content=self.display_control, height=None),
        ])
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
        def kb_left(event):
            if not self.menu_mode:
                self.api.set_instrument_prev()
                self._update_display()

        @kb.add('right')
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

        # Show current (keep for backwards compatibility)
        @kb.add('c-k')
        def kb_get_current(event):
            self._update_display()

        # Build main application
        self.application = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True
        )

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

    def _get_display_text(self):
        """Generate display text based on current mode"""
        if self.menu_mode:
            return self._get_menu_text()
        else:
            return self._get_normal_text()

    def _get_normal_text(self):
        """Generate normal mode display"""
        instrument = self.api.get_current_instrument()
        preset = self.api.get_current_preset_display_name()

        return HTML(
            f"<b><ansiblue>╔══════════════════════════════════════════════════════════════╗</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>  <ansicyan><u>Pi-Pianoteq CLI</u></ansicyan>                                          <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>╠══════════════════════════════════════════════════════════════╣</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>  <b>Instrument:</b> <ansigreen>{instrument:<45}</ansigreen> <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>  <b>Preset:</b>     <ansiyellow>{preset:<45}</ansiyellow> <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>╠══════════════════════════════════════════════════════════════╣</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>  <u>Controls:</u>                                                  <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>    ↑/↓ or Ctrl-P/N  : Navigate presets                      <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>    ←/→              : Quick instrument switch               <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>    <b>i</b> or Ctrl-I      : Open instrument menu                 <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>    Ctrl-K           : Refresh display                       <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>    <b>q</b> or Ctrl-C      : Quit                                  <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>\n"
            f"<b><ansiblue>╚══════════════════════════════════════════════════════════════╝</ansiblue></b>\n"
        )

    def _get_menu_text(self):
        """Generate menu mode display"""
        lines = [
            "<b><ansiblue>╔══════════════════════════════════════════════════════════════╗</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>  <ansicyan><u>Select Instrument</u></ansicyan>                                        <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>╠══════════════════════════════════════════════════════════════╣</ansiblue></b>",
        ]

        # Calculate visible range
        start_idx = self.menu_scroll_offset
        end_idx = min(start_idx + self.menu_visible_items, len(self.instrument_names))

        # Add scroll indicator if needed
        if start_idx > 0:
            lines.append("<b><ansiblue>║</ansiblue>  <ansigray>... (↑ for more)</ansigray>                                      <ansiblue>║</ansiblue></b>")
        else:
            lines.append("<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>")

        # Add visible menu items
        for i in range(start_idx, end_idx):
            instrument = self.instrument_names[i]
            # Truncate long names
            display_name = instrument[:52] if len(instrument) > 52 else instrument

            if i == self.current_menu_index:
                # Highlight selected item
                padding = 52 - len(display_name)
                lines.append(
                    f"<b><ansiblue>║</ansiblue>  <b><ansicyan>▶ {display_name}</ansicyan></b>{' ' * padding}  <ansiblue>║</ansiblue></b>"
                )
            else:
                padding = 54 - len(display_name)
                lines.append(
                    f"<b><ansiblue>║</ansiblue>    {display_name}{' ' * padding}<ansiblue>║</ansiblue></b>"
                )

        # Fill remaining space if needed
        displayed_items = end_idx - start_idx
        if start_idx > 0:
            displayed_items += 1  # Account for "..." line

        for _ in range(self.menu_visible_items - displayed_items):
            lines.append("<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>")

        # Add scroll indicator at bottom if needed
        if end_idx < len(self.instrument_names):
            lines.append("<b><ansiblue>║</ansiblue>  <ansigray>... (↓ for more)</ansigray>                                      <ansiblue>║</ansiblue></b>")
        else:
            lines.append("<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>")

        lines.extend([
            "<b><ansiblue>╠══════════════════════════════════════════════════════════════╣</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>  <u>Menu Controls:</u>                                            <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>    ↑/↓              : Navigate menu                          <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>    <b>Enter</b>            : Select instrument                      <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>    <b>Esc</b> or <b>q</b> or Ctrl-C: Exit menu                         <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>║</ansiblue>                                                              <ansiblue>║</ansiblue></b>",
            "<b><ansiblue>╚══════════════════════════════════════════════════════════════╝</ansiblue></b>",
        ])

        return HTML("\n".join(lines))

    def _update_display(self):
        """Force display refresh"""
        self.application.invalidate()

    def start(self):
        self.application.run()
