from PIL import Image, ImageDraw

from pi_pianoteq.client.ClientApi import ClientApi

from gfxhat import touch
from pi_pianoteq.client.gfxhat.Backlight import Backlight


class InstrumentDisplay:
    def __init__(self, api: ClientApi, width, height, font, on_enter):
        self.api = api
        self.width = width
        self.height = height
        self.font = font
        self.on_enter = on_enter
        self.preset = self.api.get_current_preset()
        self.instrument = self.api.get_current_instrument()
        self.background_primary = self.api.get_current_background_primary()
        self.background_secondary = self.api.get_current_background_secondary()
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw_text()
        self.backlight = Backlight("000000")
        self.set_backlight()

    def draw_text(self):
        self.image.paste(0, (0, 0, self.width, self.height))
        width_preset, height_preset = self.font.getsize(self.preset)
        width_instrument, height_instrument = self.font.getsize(self.instrument)

        a = 0
        b = (self.height - height_preset) // 2
        c = (self.width - width_instrument) // 2
        d = 0
        self.draw.text((a, b), self.preset, 1, self.font)
        self.draw.text((c, d), self.instrument, 1, self.font)

    def get_backlight(self):
        return self.backlight

    def set_backlight(self):
        for i in range(6):
            if i == 0 or i == 5:
                self.backlight.set_backlight(self.background_secondary, i)
            else:
                self.backlight.set_backlight(self.background_primary, i)

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
            if ch == touch.ENTER:
                self.on_enter()
            self.update_display()

        return handler

    def get_image(self):
        return self.image

    def update_display(self):
        self.preset = self.api.get_current_preset()
        self.instrument = self.api.get_current_instrument()
        self.background_primary = self.api.get_current_background_primary()
        self.background_secondary = self.api.get_current_background_secondary()
        self.draw_text()
        self.set_backlight()
