import signal

from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class GfxhatClient(Client):

    def __init__(self, api: ClientApi):
        super().__init__(api)
        self.preset = self.api.get_current_preset()
        self.instrument = self.api.get_current_instrument()
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
        w_p, h_p = self.font.getsize(self.preset)
        w_i, h_i = self.font.getsize(self.instrument)

        a = (self.width - w_p) // 2
        b = (self.height - h_p) // 2
        c = (self.width - w_i) // 2
        d = 0
        self.draw.text((a, b), self.preset, 1, self.font)
        self.draw.text((c, d), self.instrument, 1, self.font)
        for x in range(128):
            for y in range(64):
                pixel = self.image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)
        lcd.show()

    def get_handler(self):
        def handler(ch, event):
            if event != 'press':
                return
            if ch == touch.DOWN:
                self.api.set_preset_next()
            if ch == touch.UP:
                self.api.set_preset_prev()
            if ch == touch.LEFT:
                self.api.set_instrument_prev()
            if ch == touch.RIGHT:
                self.api.set_instrument_next()
            self.preset = self.api.get_current_preset()
            self.instrument = self.api.get_current_instrument()
            self.draw_text()
        return handler

    @staticmethod
    def cleanup(signal_number, stack_frame):
        backlight.set_all(0, 0, 0)
        backlight.show()
        lcd.clear()
        lcd.show()
