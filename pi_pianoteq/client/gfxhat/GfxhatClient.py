import signal

from gfxhat import touch, lcd, backlight, fonts
from PIL import ImageFont, Image
import time

from pi_pianoteq.client.gfxhat.InstrumentDisplay import InstrumentDisplay
from pi_pianoteq.client.gfxhat.InstrumentMenuDisplay import InstrumentMenuDisplay
from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class GfxhatClient(Client):

    def __init__(self, api: ClientApi):
        super().__init__(api)
        self.interrupt = False
        self.menu_open = False
        self.width, self.height = lcd.dimensions()
        font = ImageFont.truetype(fonts.BitbuntuFull, 10)
        self.instrument_display = InstrumentDisplay(api, self.width, self.height, font, self.on_enter_menu)
        self.menu_display = InstrumentMenuDisplay(api, self.width, self.height, font, self.on_exit_menu)

    def start(self):
        for index in range(6):
            touch.set_led(index, 0)
            touch.on(index, self.instrument_display.get_handler())

        signal.signal(signal.SIGTERM, self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)
        while True:
            self.get_display().get_backlight().apply_backlight()
            self.blit_image()
            backlight.show()
            lcd.show()
            time.sleep(1.0 / 30)
            if self.interrupt:
                break

    def update_handler(self):
        if self.menu_open:
            self.set_handler(self.menu_display.get_handler())
        else:
            self.set_handler(self.instrument_display.get_handler())

    @staticmethod
    def set_handler(handler):
        for index in range(6):
            touch.on(index, handler)

    def get_display(self):
        if self.menu_open:
            return self.menu_display
        else:
            return self.instrument_display

    def blit_image(self):
        for x in range(128):
            for y in range(64):
                pixel = self.get_display().get_image().getpixel((x, y))
                lcd.set_pixel(x, y, pixel)

    def cleanup(self, signal_number, stack_frame):
        self.interrupt = True
        backlight.set_all(0, 0, 0)
        backlight.show()
        lcd.clear()
        lcd.show()

    def on_enter_menu(self):
        self.menu_open = True
        self.menu_display.update_instrument()
        self.update_handler()

    def on_exit_menu(self):
        self.menu_open = False
        self.update_handler()
        self.instrument_display.update_display()
