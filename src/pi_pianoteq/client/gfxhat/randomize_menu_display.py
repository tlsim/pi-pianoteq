from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


class RandomizeMenuDisplay(MenuDisplay):
    """
    Randomization submenu with options for different randomization modes.

    Contains:
    - Randomize Preset: Randomize parameters of current preset
    - Random All: Random instrument + preset + randomized parameters
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, on_randomize_preset, on_randomize_all):
        self.on_randomize_preset = on_randomize_preset
        self.on_randomize_all = on_randomize_all
        super().__init__(api, width, height, font, on_exit)

    def get_menu_options(self):
        return [
            MenuOption("Randomize Preset", self.on_randomize_preset, self.font),
            MenuOption("Random All", self.on_randomize_all, self.font)
        ]

    def get_heading(self):
        return "Randomize:"
