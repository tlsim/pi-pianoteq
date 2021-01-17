from PIL import Image, ImageDraw

from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.client.gfxhat.Backlight import Backlight
from pi_pianoteq.client.gfxhat.MenuOption import MenuOption
from gfxhat import touch


class MenuDisplay:
    def __init__(self, api: ClientApi, width, height, font, on_exit):
        self.width = width
        self.height = height
        self.api = api
        self.font = font
        self.on_exit = on_exit
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.menu_options = self.get_menu_options()
        self.current_menu_option = 0
        self.selected_menu_option = 0
        self.backlight = Backlight("#cccccc")
        self.draw_image()

    def get_menu_options(self):
        instrument_names = self.api.get_instrument_names()
        return [MenuOption(i, self.set_instrument, self.font, (i,)) for i in instrument_names]

    def set_backlight(self, hex_colour):
        self.backlight.set_all_backlights(hex_colour)

    def set_instrument(self, name):
        self.api.set_instrument(name)
        self.on_exit()

    def draw_image(self):
        self.image.paste(0, (0, 0, self.width, self.height))
        offset_top = 0

        for index in range(len(self.menu_options)):
            if index == self.current_menu_option:
                break
            offset_top += 12

        for index in range(len(self.menu_options)):
            x = 10
            y = (index * 12) + (self.height / 2) - 4 - offset_top
            option = self.menu_options[index]
            if index == self.current_menu_option:
                self.draw.rectangle(((x-2, y-1), (self.width, y+10)), 1)
            self.draw.text((x, y), option.name, 0 if index == self.current_menu_option else 1, self.font)

        w, h = self.font.getsize('>')
        self.draw.text((0, (self.height - h) / 2), '>', 1, self.font)

    def update_instrument(self):
        current_instrument = self.api.get_current_instrument()
        current_option = next((o for o in self.menu_options if o.name == current_instrument), None)
        if current_option is not None:
            self.current_menu_option = self.menu_options.index(current_option)
            self.draw_image()

    def get_handler(self):
        def handler(ch, event):
            if event != 'press':
                return
            if ch == touch.BACK:
                self.current_menu_option = self.selected_menu_option
                self.on_exit()
            if ch == touch.UP:
                self.current_menu_option -= 1
            if ch == touch.DOWN:
                self.current_menu_option += 1
            if ch == touch.LEFT:
                pass
            if ch == touch.RIGHT:
                pass
            if ch == touch.ENTER:
                self.menu_options[self.current_menu_option].trigger()
                self.selected_menu_option = self.current_menu_option
            self.current_menu_option %= len(self.menu_options)
            self.draw_image()

        return handler
