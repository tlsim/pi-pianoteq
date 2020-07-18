from PIL import Image, ImageDraw

from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.client.gfxhat.Backlight import Backlight
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
        self.text = "Menu"
        self.backlight = Backlight("#cccccc")
        self.draw_text()

    def draw_text(self):
        self.image.paste(0, (0, 0, self.width, self.height))
        width_text, height_text = self.font.getsize(self.text)

        a = (self.width - width_text) // 2
        b = (self.height - height_text) // 2
        self.draw.text((a, b), self.text, 1, self.font)

    def get_handler(self):
        def handler(ch, event):
            if event != 'press':
                return
            if ch == touch.BACK:
                self.on_exit()
            if ch == touch.UP:
                pass
            if ch == touch.LEFT:
                pass
            if ch == touch.RIGHT:
                pass
            if ch == touch.ENTER:
                pass

        return handler
