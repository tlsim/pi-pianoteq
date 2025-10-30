import signal

from gfxhat import touch, lcd, backlight, fonts
from PIL import ImageFont, Image, ImageDraw
import time
from typing import Optional

from pi_pianoteq.client.gfxhat.InstrumentDisplay import InstrumentDisplay
from pi_pianoteq.client.gfxhat.InstrumentMenuDisplay import InstrumentMenuDisplay
from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class GfxhatClient(Client):
    """
    GFX HAT hardware client with loading screen support.

    Loading mode (api=None): Shows simple loading messages with blue backlight
    Normal mode (after set_api): Full instrument/preset display
    """

    # Loading screen colors
    LOADING_BACKLIGHT_COLOR = '#1e3a5f'  # Calming blue

    def __init__(self, api: Optional[ClientApi]):
        super().__init__(api)
        self.interrupt = False
        self.menu_open = False
        self.width, self.height = lcd.dimensions()
        self.font = ImageFont.truetype(fonts.BitbuntuFull, 10)

        # Loading mode state
        self.loading_mode = (api is None)
        self.loading_message = ""
        self.loading_image = Image.new('P', (self.width, self.height))
        self.loading_draw = ImageDraw.Draw(self.loading_image)

        # Normal mode displays (initialized later if api provided)
        self.instrument_display = None
        self.menu_display = None

        if api is not None:
            self._init_normal_displays()

    def _init_normal_displays(self):
        """Initialize normal operation displays (requires API)"""
        self.api.set_on_exit(self.cleanup)
        self.instrument_display = InstrumentDisplay(
            self.api, self.width, self.height, self.font, self.on_enter_menu
        )
        self.menu_display = InstrumentMenuDisplay(
            self.api, self.width, self.height, self.font, self.on_exit_menu
        )
        self.loading_mode = False

    def set_api(self, api: ClientApi):
        """Provide API and initialize normal displays"""
        self.api = api
        self._init_normal_displays()

    def show_loading_message(self, message: str):
        """Display a loading message on the LCD with blue backlight"""
        self.loading_message = message

        # Clear display
        self.loading_image.paste(0, (0, 0, self.width, self.height))

        # Draw centered text
        bbox = self.font.getbbox(message)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        self.loading_draw.text((x, y), message, 1, self.font)

        # Set blue backlight
        r, g, b = self._hex_to_rgb(self.LOADING_BACKLIGHT_COLOR)
        for i in range(6):
            backlight.set_pixel(i, r, g, b)

        # Display
        self._blit_loading_image()
        backlight.show()
        lcd.show()

    def clear_loading_screen(self):
        """Clear loading screen (prepare for normal display)"""
        lcd.clear()
        lcd.show()
        for i in range(6):
            backlight.set_pixel(i, 0, 0, 0)
        backlight.show()

    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def start(self):
        """Start normal client operation (requires API)"""
        if self.loading_mode:
            raise RuntimeError("Cannot start client in loading mode. Call set_api() first.")

        for index in range(6):
            touch.set_led(index, 0)
            touch.on(index, self.instrument_display.get_handler())

        signal.signal(signal.SIGTERM, lambda signal_num, stack_frame: self.cleanup())
        signal.signal(signal.SIGINT, lambda signal_num, stack_frame: self.cleanup())

        # Start scrolling for instrument display
        self.instrument_display.start_scrolling()

        while True:
            # Redraw display to pick up scroll offset changes
            display = self.get_display()
            if hasattr(display, 'draw_text'):
                display.draw_text()
            elif hasattr(display, 'draw_image'):
                display.draw_image()

            display.get_backlight().apply_backlight()
            self.blit_image()
            backlight.show()
            lcd.show()
            time.sleep(1.0 / 30)
            if self.interrupt:
                break
        time.sleep(2.0)

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

    def _blit_loading_image(self):
        """Blit loading image to LCD"""
        for x in range(128):
            for y in range(64):
                pixel = self.loading_image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)

    def cleanup(self):
        self.interrupt = True
        # Stop all scrolling threads (if displays are initialized)
        if self.instrument_display:
            self.instrument_display.stop_scrolling()
        if self.menu_display:
            self.menu_display.stop_scrolling()
        time.sleep(1.0)
        backlight.set_all(0, 0, 0)
        backlight.show()
        lcd.clear()
        lcd.show()

    def on_enter_menu(self):
        self.instrument_display.stop_scrolling()
        self.menu_open = True
        self.menu_display.update_instrument()
        self.menu_display.start_scrolling()
        self.update_handler()

    def on_exit_menu(self):
        self.menu_display.stop_scrolling()
        self.menu_open = False
        self.update_handler()
        self.instrument_display.update_display()
        self.instrument_display.start_scrolling()
