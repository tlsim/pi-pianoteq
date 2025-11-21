from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay
from pi_pianoteq.client.gfxhat.shutdown_display import ShutdownDisplay
from gfxhat import touch


class ControlMenuDisplay(MenuDisplay):
    """
    Top-level control menu with options for various functions.

    Currently contains:
    - Select Instrument: Opens instrument selection menu
    - Shut down: Opens shutdown confirmation menu
    """

    def __init__(self, api: ClientApi, width, height, font, on_exit, on_select_instrument):
        self.on_select_instrument = on_select_instrument
        super().__init__(api, width, height, font, on_exit)
        self.shutdown_menu_open = False
        self.shutdown_display = ShutdownDisplay(api, width, height, font, self.on_exit_menu)

    def get_menu_options(self):
        return [
            MenuOption("Select Instrument", self.on_select_instrument, self.font),
            MenuOption("Shut down", self.on_enter_menu, self.font)
        ]

    def get_heading(self):
        return "Menu:"

    def get_image(self):
        if self.shutdown_menu_open:
            return self.shutdown_display.get_image()
        else:
            return self.image

    def get_backlight(self):
        if self.shutdown_menu_open:
            return self.shutdown_display.get_backlight()
        else:
            return self.backlight

    @staticmethod
    def set_handler(handler):
        for index in range(6):
            touch.on(index, handler)

    def update_handler(self):
        if self.shutdown_menu_open:
            self.set_handler(self.shutdown_display.get_handler())
        else:
            self.set_handler(self.get_handler())

    def on_enter_menu(self):
        self.shutdown_menu_open = True
        self.update_handler()

    def on_exit_menu(self):
        self.shutdown_menu_open = False
        self.update_handler()
