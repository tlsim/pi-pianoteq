from PIL import Image, ImageDraw

from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.client.gfxhat.Backlight import Backlight
from pi_pianoteq.client.gfxhat.MenuOption import MenuOption
from pi_pianoteq.client.gfxhat.MenuDisplay import MenuDisplay
from pi_pianoteq.client.gfxhat.ShutdownDisplay import ShutdownDisplay
from gfxhat import touch


class InstrumentMenuDisplay(MenuDisplay):
    def __init__(self, api: ClientApi, width, height, font, on_exit):
        super().__init__(api, width, height, font, on_exit)
        self.menu_open = False
        self.shutdown_display = ShutdownDisplay(api, width, height, font, self.on_exit_menu)

    def get_menu_options(self):
        instrument_names = self.api.get_instrument_names()
        menu_options = [MenuOption(i, self.set_instrument, self.font, (i,)) for i in instrument_names]
        shutdown_option = MenuOption("Shut down", self.on_enter_menu, self.font)
        menu_options.append(shutdown_option)
        return menu_options

    def set_instrument(self, name):
        self.api.set_instrument(name)
        self.on_exit()

    def update_instrument(self):
        current_instrument = self.api.get_current_instrument()
        current_option = next((o for o in self.menu_options if o.name == current_instrument), None)
        if current_option is not None:
            self.current_menu_option = self.menu_options.index(current_option)
            self._update_selected_option()
            self.draw_image()

    def get_image(self):
        if self.menu_open:
            return self.shutdown_display.get_image()
        else:
            return self.image

    def get_backlight(self):
        if self.menu_open:
            return self.shutdown_display.get_backlight()
        else:
            return self.backlight

    @staticmethod
    def set_handler(handler):
        for index in range(6):
            touch.on(index, handler)

    def update_handler(self):
        if self.menu_open:
            self.set_handler(self.shutdown_display.get_handler())
        else:
            self.set_handler(self.get_handler())

    def on_enter_menu(self):
        self.menu_open = True
        self.update_handler()

    def on_exit_menu(self):
        self.menu_open = False
        self.update_handler()
