from PIL import Image, ImageDraw

from pi_pianoteq.client.gfxhat.MenuOption import MenuOption
from pi_pianoteq.client.gfxhat.Backlight import Backlight

from gfxhat import touch


class MenuDisplay:
    def __init__(self, api, width, height, font, on_exit):
        self.api = api
        self.width = width
        self.height = height
        self.font = font
        self.on_exit = on_exit
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.menu_options = self.get_menu_options()
        self.backlight = Backlight("#cccccc")
        self.current_menu_option = 0
        self.selected_menu_option = 0
        self.draw_image()

    def get_menu_options(self):
        raise NotImplemented

    def get_backlight(self):
        return self.backlight

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
                self.current_menu_option -= 1
            if ch == touch.RIGHT:
                self.current_menu_option += 1
            if ch == touch.ENTER:
                self.menu_options[self.current_menu_option].trigger()
                self.selected_menu_option = self.current_menu_option
            self.current_menu_option %= len(self.menu_options)
            self.draw_image()

        return handler

    def get_image(self):
        return self.image
