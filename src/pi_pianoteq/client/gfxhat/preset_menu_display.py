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
        self.ignore_next_release = True
        self.preset_selected = False
        super().__init__(api, width, height, font, on_exit)
        self.update_preset()

    def get_menu_options(self):
        """Build menu options with presets followed by 'Randomise' as last option."""
        options = []

        # Add all presets for this instrument
        presets = self.api.get_presets(self.instrument_name)
        for preset in presets:
            options.append(MenuOption(preset.display_name, self.set_preset, self.font, (preset.name,)))

        # Add "Randomise" as last option
        options.append(MenuOption("Randomise", self.randomize_preset, self.font))

        return options

    def get_heading(self):
        return "Select Preset:"

    def set_preset(self, preset_name):
        """Load selected preset and exit menu."""
        self.preset_selected = True
        self.api.set_preset(self.instrument_name, preset_name)
        self.on_exit()

    def randomize_preset(self):
        """Randomize preset for this instrument and mark for menu exit."""
        # If we're viewing a different instrument's presets, switch to it first
        if self.instrument_name != self.api.get_current_instrument().name:
            # Switch to this instrument by loading its first preset
            presets = self.api.get_presets(self.instrument_name)
            if presets:
                first_preset = presets[0]
                self.api.set_preset(self.instrument_name, first_preset.name)

        # Now randomize the current preset
        self.api.randomize_current_preset()
        self.preset_selected = True
        self.on_exit()

    def update_preset(self):
        """Highlight currently loaded preset if viewing current instrument's presets."""
        if self.instrument_name == self.api.get_current_instrument().name:
            current_preset = self.api.get_current_preset()
            # Compare raw names (stored in options[0]), not display names
            # Search all options except last (Randomise)
            current_option = next((o for o in self.menu_options[:-1]
                                  if o.options and o.options[0] == current_preset.name), None)
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
