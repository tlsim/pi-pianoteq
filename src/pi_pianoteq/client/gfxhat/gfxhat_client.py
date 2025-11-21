import signal
import logging

from gfxhat import touch, lcd, backlight, fonts
from PIL import ImageFont
import time
from typing import Optional

from pi_pianoteq.client.gfxhat.instrument_display import InstrumentDisplay
from pi_pianoteq.client.gfxhat.instrument_menu_display import InstrumentMenuDisplay
from pi_pianoteq.client.gfxhat.control_menu_display import ControlMenuDisplay
from pi_pianoteq.client.gfxhat.loading_display import LoadingDisplay
from pi_pianoteq.client.gfxhat.preset_menu_display import PresetMenuDisplay
from pi_pianoteq.client.client import Client
from pi_pianoteq.client.client_api import ClientApi


class GfxhatClient(Client):
    """
    GFX HAT hardware client with loading screen support.

    Loading mode (api=None): Shows simple loading messages with blue backlight
    Normal mode (after set_api): Full instrument/preset display
    """

    def __init__(self, api: Optional[ClientApi]):
        super().__init__(api)
        self.interrupt = False
        self.control_menu_open = False
        self.instrument_menu_open = False
        self.preset_menu_open = False
        self.preset_menu_source = None
        self.width, self.height = lcd.dimensions()
        self.font = ImageFont.truetype(fonts.BitbuntuFull, 10)

        # Loading mode state
        self.loading_mode = (api is None)

        # Create loading display (used during startup)
        self.loading_display = LoadingDisplay(self.width, self.height, self.font)

        # Normal mode displays (initialized later if api provided)
        self.instrument_display = None
        self.control_menu_display = None
        self.menu_display = None
        self.preset_menu_display = None

        if api is not None:
            self._init_normal_displays()

    def _init_normal_displays(self):
        """Initialize normal operation displays (requires API)"""
        self.api.set_on_exit(self.cleanup)
        self.instrument_display = InstrumentDisplay(
            self.api, self.width, self.height, self.font,
            self.on_enter_control_menu,
            self.on_enter_preset_menu_from_main
        )
        self.control_menu_display = ControlMenuDisplay(
            self.api, self.width, self.height, self.font,
            self.on_exit_control_menu,
            self.on_enter_instrument_menu,
            self.on_randomize_preset,
            self.on_random_all
        )
        self.menu_display = InstrumentMenuDisplay(
            self.api, self.width, self.height, self.font,
            self.on_exit_instrument_menu,
            self.on_enter_preset_menu_from_instrument_menu
        )
        self.loading_mode = False

    def set_api(self, api: ClientApi):
        """Provide API and initialize normal displays"""
        self.api = api
        self._init_normal_displays()

    def show_loading_message(self, message: str):
        """Display a loading message on the LCD with blue backlight"""
        self.loading_display.set_message(message)
        # Force immediate display update
        self.loading_display.get_backlight().apply_backlight()
        self.blit_image()
        backlight.show()
        lcd.show()

    def start(self):
        """Start normal client operation (requires API)"""
        if self.loading_mode:
            raise RuntimeError("Cannot start client in loading mode. Call set_api() first.")

        # Enable held events for long press detection
        touch.enable_repeat(True)

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
        if self.preset_menu_open:
            self.set_handler(self.preset_menu_display.get_handler())
        elif self.instrument_menu_open:
            self.set_handler(self.menu_display.get_handler())
        elif self.control_menu_open:
            self.set_handler(self.control_menu_display.get_handler())
        else:
            self.set_handler(self.instrument_display.get_handler())

    @staticmethod
    def set_handler(handler):
        for index in range(6):
            touch.on(index, handler)

    def get_display(self):
        """Get current active display (loading, preset menu, instrument menu, control menu, or instrument)"""
        if self.loading_mode:
            return self.loading_display
        elif self.preset_menu_open:
            return self.preset_menu_display
        elif self.instrument_menu_open:
            return self.menu_display
        elif self.control_menu_open:
            return self.control_menu_display
        else:
            return self.instrument_display

    def blit_image(self):
        for x in range(128):
            for y in range(64):
                pixel = self.get_display().get_image().getpixel((x, y))
                lcd.set_pixel(x, y, pixel)

    def cleanup(self):
        self.interrupt = True
        # Stop all scrolling threads (if displays are initialized)
        if self.instrument_display:
            self.instrument_display.stop_scrolling()
        if self.control_menu_display:
            self.control_menu_display.stop_scrolling()
        if self.menu_display:
            self.menu_display.stop_scrolling()
        if self.preset_menu_display:
            self.preset_menu_display.stop_scrolling()
        time.sleep(1.0)
        backlight.set_all(0, 0, 0)
        backlight.show()
        lcd.clear()
        lcd.show()

    def on_enter_control_menu(self):
        self.instrument_display.stop_scrolling()
        self.control_menu_open = True
        self.control_menu_display.start_scrolling()
        self.update_handler()

    def on_exit_control_menu(self):
        self._close_control_menu_and_return_to_main()

    def _close_control_menu_and_return_to_main(self):
        """Close control menu and return to main instrument display."""
        if self.control_menu_open:
            self.control_menu_display.stop_scrolling()
            self.control_menu_open = False

        self.instrument_display.update_display()
        self.instrument_display.start_scrolling()
        self.update_handler()

    def on_enter_instrument_menu(self):
        self.control_menu_display.stop_scrolling()
        self.instrument_menu_open = True
        self.menu_display.update_instrument()
        self.menu_display.start_scrolling()
        self.update_handler()

    def on_exit_instrument_menu(self):
        self.menu_display.stop_scrolling()
        self.instrument_menu_open = False

        # If an instrument was selected, close all menus and return to main display
        # Otherwise (BACK pressed), return to control menu
        if self.menu_display.instrument_selected:
            self.menu_display.instrument_selected = False
            if self.control_menu_open:
                self.control_menu_display.stop_scrolling()
                self.control_menu_open = False
            self.instrument_display.update_display()
            self.instrument_display.start_scrolling()
        else:
            self.control_menu_display.start_scrolling()

        self.update_handler()

    def on_randomize_preset(self):
        """Randomize parameters of current preset and return to main display."""
        self.api.randomize_current_preset()
        self._close_control_menu_and_return_to_main()

    def on_random_all(self):
        """Randomly select instrument and preset, randomize parameters, and return to main display."""
        self.api.randomize_all()
        self._close_control_menu_and_return_to_main()

    def on_enter_preset_menu_from_main(self):
        """Long press ENTER on main display - show presets for current instrument."""
        instrument_name = self.api.get_current_instrument().name
        self._open_preset_menu(instrument_name, source='main')

    def on_enter_preset_menu_from_instrument_menu(self, instrument_name):
        """Long press ENTER on instrument menu item - show presets for highlighted instrument."""
        self._open_preset_menu(instrument_name, source='instrument_menu')

    def _open_preset_menu(self, instrument_name, source):
        """Common preset menu opening logic."""
        if source == 'main':
            self.instrument_display.stop_scrolling()
        else:
            self.menu_display.stop_scrolling()

        self.preset_menu_display = PresetMenuDisplay(
            self.api, self.width, self.height, self.font,
            self.on_exit_preset_menu, instrument_name
        )

        self.preset_menu_open = True
        self.preset_menu_source = source
        self.preset_menu_display.start_scrolling()
        self.update_handler()

    def on_exit_preset_menu(self):
        """Exit preset menu and return to previous display."""
        self.preset_menu_display.stop_scrolling()
        self.preset_menu_open = False

        # If a preset was selected, always return to main display
        # Otherwise (BACK pressed), return to source
        if self.preset_menu_display.preset_selected:
            # Close all menus if they were open
            if self.instrument_menu_open:
                self.menu_display.stop_scrolling()
                self.instrument_menu_open = False
            if self.control_menu_open:
                self.control_menu_display.stop_scrolling()
                self.control_menu_open = False
            self.instrument_display.update_display()
            self.instrument_display.start_scrolling()
        elif self.preset_menu_source == 'main':
            self.instrument_display.update_display()
            self.instrument_display.start_scrolling()
        else:
            self.menu_display.start_scrolling()

        self.update_handler()

    def get_logging_handler(self) -> Optional[logging.Handler]:
        """Return None to use default stdout/stderr handlers"""
        return None
