from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


class ControlMenuDisplay(MenuDisplay):
    """
    Top-level control menu with options for various functions.

    Currently contains:
    - Select Instrument: Opens instrument selection menu
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, on_select_instrument):
        self.on_select_instrument = on_select_instrument
        super().__init__(api, width, height, font, on_exit)

    def get_menu_options(self):
        return [
            MenuOption("Select Instrument", self.on_select_instrument, self.font)
        ]

    def get_heading(self):
        return "Menu:"
