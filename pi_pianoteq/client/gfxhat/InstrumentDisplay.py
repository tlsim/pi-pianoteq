from PIL import Image, ImageDraw

from pi_pianoteq.client.ClientApi import ClientApi

from gfxhat import touch
from pi_pianoteq.client.gfxhat.Backlight import Backlight
from pi_pianoteq.client.gfxhat.ScrollingText import ScrollingText


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

        # Create scrolling text instances
        # Slower, more leisurely scrolling: 1px per update, every 200ms
        self.preset_scroller = ScrollingText(
            self.preset, self.font, self.width - 5,
            scroll_speed=1, update_interval=0.2
        )
        self.instrument_scroller = ScrollingText(
            self.instrument, self.font, self.width - 5,
            scroll_speed=1, update_interval=0.2
        )

        self.draw_text()
        self.backlight = Backlight("000000")
        self.set_backlight()

    def draw_text(self):
        self.image.paste(0, (0, 0, self.width, self.height))

        # Calculate heights for positioning
        bbox_preset = self.font.getbbox(self.preset)
        height_preset = bbox_preset[3] - bbox_preset[1]
        bbox_instrument = self.font.getbbox(self.instrument)
        height_instrument = bbox_instrument[3] - bbox_instrument[1]

        # Get scroll offsets
        preset_offset = self.preset_scroller.get_offset()
        instrument_offset = self.instrument_scroller.get_offset()

        # Draw instrument at top, scrolling from left
        instrument_x = 2 - instrument_offset
        instrument_y = 0
        self.draw.text((instrument_x, instrument_y), self.instrument, 1, self.font)

        # Draw preset at vertical center, scrolling from left
        preset_x = 2 - preset_offset
        preset_y = (self.height - height_preset) // 2
        self.draw.text((preset_x, preset_y), self.preset, 1, self.font)

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

        # Update scrolling text instances
        self.preset_scroller.update_text(self.preset)
        self.instrument_scroller.update_text(self.instrument)

        self.draw_text()
        self.set_backlight()

    def start_scrolling(self):
        """Start scrolling animation for long text."""
        self.preset_scroller.start()
        self.instrument_scroller.start()

    def stop_scrolling(self):
        """Stop scrolling animation."""
        self.preset_scroller.stop()
        self.instrument_scroller.stop()
