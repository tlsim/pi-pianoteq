from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


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
        super().__init__(api, width, height, font, on_exit)
        self.update_preset()

    def get_menu_options(self):
        """Build menu options from preset names for this instrument."""
        preset_names = self.api.get_preset_names(self.instrument_name)
        return [MenuOption(name, self.set_preset, self.font, (name,))
                for name in preset_names]

    def set_preset(self, preset_name):
        """Load selected preset and exit menu."""
        self.api.set_preset(self.instrument_name, preset_name)
        self.on_exit()

    def update_preset(self):
        """Highlight currently loaded preset if viewing current instrument's presets."""
        if self.instrument_name == self.api.get_current_instrument():
            current_preset = self.api.get_current_preset()
            current_option = next((o for o in self.menu_options if o.name == current_preset), None)
            if current_option is not None:
                self.current_menu_option = self.menu_options.index(current_option)
                self._update_selected_option()
                self.draw_image()
