from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay
from pi_pianoteq.instrument.preset import Preset


class PresetMenuDisplay(MenuDisplay):
    """
    Menu display for selecting presets within a specific instrument.

    Shows list of presets for the given instrument, with scrolling support
    for long preset names. Extends MenuDisplay base class pattern.
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, instrument_name: str):
        """
        Initialize preset menu for a specific instrument.

        Args:
            api: Client API instance
            width: Display width in pixels
            height: Display height in pixels
            font: Font for rendering text
            on_exit: Callback when exiting menu
            instrument_name: Name of instrument whose presets to display
        """
        self.instrument_name = instrument_name
        self.ignore_next_release = True
        super().__init__(api, width, height, font, on_exit)
        self.update_preset()

    def get_menu_options(self):
        """Build menu options from preset names for this instrument."""
        preset_names = self.api.get_preset_names(self.instrument_name)
        preset_prefix = self.api.get_instrument_preset_prefix(self.instrument_name)

        options = []
        for raw_name in preset_names:
            preset = Preset(raw_name)
            display_name = preset.get_display_name(preset_prefix)
            options.append(MenuOption(display_name, self.set_preset, self.font, (raw_name,)))

        return options

    def set_preset(self, preset_name):
        """Load selected preset and exit menu."""
        self.api.set_preset(self.instrument_name, preset_name)
        self.on_exit()

    def update_preset(self):
        """Highlight currently loaded preset if viewing current instrument's presets."""
        if self.instrument_name == self.api.get_current_instrument():
            current_preset = self.api.get_current_preset()
            # Compare raw names (stored in options[0]), not display names
            current_option = next((o for o in self.menu_options
                                  if o.options and o.options[0] == current_preset), None)
            if current_option is not None:
                self.current_menu_option = self.menu_options.index(current_option)
                self._update_selected_option()
                self.draw_image()

    def get_handler(self):
        """Get button handler, ignoring first ENTER release after menu opens."""
        from gfxhat import touch
        base_handler = super().get_handler()

        def handler(ch, event):
            if event == 'release' and ch == touch.ENTER:
                if self.ignore_next_release:
                    self.ignore_next_release = False
                    return

            base_handler(ch, event)

        return handler
