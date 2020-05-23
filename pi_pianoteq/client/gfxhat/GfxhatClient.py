import signal

from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class GfxhatClient(Client):

    def __init__(self, api: ClientApi):
        super().__init__(api)
        self.text = self.api.get_current_preset()
        self.width, self.height = lcd.dimensions()
        self.font = ImageFont.truetype(fonts.BitbuntuFull, 10)
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def start(self):
        for index in range(6):
            touch.set_led(index, 0)
            backlight.set_pixel(index, 255, 255, 255)
            touch.on(index, self.get_handler())
        backlight.show()

        signal.signal(signal.SIGTERM, self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)
        self.draw_text()
        signal.pause()

    def draw_text(self):
        self.image.paste(0, (0, 0, self.width, self.height))
        w, h = self.font.getsize(self.text)
        a = (self.width - w) // 2
        b = (self.height - h) // 2
        self.draw.text((a, b), self.text, 1, self.font)
        for x in range(128):
            for y in range(64):
                pixel = self.image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)
        lcd.show()

    def get_handler(self):
        def handler(ch, event):
            if event != 'press':
                return
            if ch == 1:
                self.api.set_preset_next()
            if ch == 0:
                self.api.set_preset_prev()
            self.text = self.api.get_current_preset()
            self.draw_text()
        return handler

    @staticmethod
    def cleanup(signal_number, stack_frame):
        backlight.set_all(0, 0, 0)
        backlight.show()
        lcd.clear()
        lcd.show()
