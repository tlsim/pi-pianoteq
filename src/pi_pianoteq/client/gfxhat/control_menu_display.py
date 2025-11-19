from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


class ControlMenuDisplay(MenuDisplay):
    """
    Top-level control menu with options for various functions.

    Contains:
    - Select Instrument: Opens instrument selection menu
    - Randomize Preset: Randomizes parameters of current preset
    - Random Instrument: Randomly selects instrument and randomizes parameters
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, on_select_instrument, on_randomize_preset, on_random_instrument):
        self.on_select_instrument = on_select_instrument
        self.on_randomize_preset = on_randomize_preset
        self.on_random_instrument = on_random_instrument
        super().__init__(api, width, height, font, on_exit)

    def get_menu_options(self):
        return [
            MenuOption("Select Instrument", self.on_select_instrument, self.font),
            MenuOption("Randomize Preset", self.on_randomize_preset, self.font),
            MenuOption("Random Instrument", self.on_random_instrument, self.font)
        ]

    def get_heading(self):
        return "Menu:"
