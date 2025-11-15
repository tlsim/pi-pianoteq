from PIL import Image, ImageDraw

from pi_pianoteq.client.client_api import ClientApi

from gfxhat import touch
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.scrolling_text import ScrollingText
from pi_pianoteq.util.button_suppression import ButtonSuppression


class InstrumentDisplay:
    """
    Main display showing current instrument and preset with scrolling text.

    Uses ScrollingText instances with background threads for smooth scrolling.
    Threads are started when this display is visible, stopped when switching to menu.
    """
    TEXT_START_X = 2
    TEXT_MARGIN = 5
    WRAP_GAP = 20

    def __init__(self, api: ClientApi, width, height, font, on_enter, on_enter_preset_menu):
        self.api = api
        self.width = width
        self.height = height
        self.font = font
        self.on_enter = on_enter
        self.on_enter_preset_menu = on_enter_preset_menu
        self.suppression = ButtonSuppression(300)
        self.held_count = {}
        self.held_threshold = 2
        current_instrument = self.api.get_current_instrument()
        self.preset = self.api.get_current_preset().display_name
        self.instrument = current_instrument.name
        self.background_primary = current_instrument.background_primary
        self.background_secondary = current_instrument.background_secondary
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.preset_scroller = ScrollingText(self.preset, self.font, self.width - self.TEXT_MARGIN)
        self.instrument_scroller = ScrollingText(self.instrument, self.font, self.width - self.TEXT_MARGIN)

        self.draw_text()
        self.backlight = Backlight("000000")
        self.set_backlight()

    def draw_text(self):
        """
        Render instrument and preset text with scrolling.

        Uses seamless marquee technique: draws text twice (at primary position
        and wrap position) so there's no visible jump when scrolling loops.
        """
        self.image.paste(0, (0, 0, self.width, self.height))

        bbox_preset = self.font.getbbox(self.preset)
        height_preset = bbox_preset[3] - bbox_preset[1]
        bbox_instrument = self.font.getbbox(self.instrument)
        height_instrument = bbox_instrument[3] - bbox_instrument[1]

        # Get current scroll offset from background threads
        preset_offset = self.preset_scroller.get_offset()
        instrument_offset = self.instrument_scroller.get_offset()

        # Draw instrument name (top of display)
        instrument_x = self.TEXT_START_X - instrument_offset
        instrument_y = 0
        self.draw.text((instrument_x, instrument_y), self.instrument, 1, self.font)
        # Draw second copy for seamless wrap if text is scrolling
        if self.instrument_scroller.needs_scrolling:
            wrap_x = instrument_x + bbox_instrument[2] - bbox_instrument[0] + self.WRAP_GAP
            self.draw.text((wrap_x, instrument_y), self.instrument, 1, self.font)

        # Draw preset name (middle of display)
        preset_x = self.TEXT_START_X - preset_offset
        preset_y = (self.height - height_preset) // 2
        self.draw.text((preset_x, preset_y), self.preset, 1, self.font)
        # Draw second copy for seamless wrap if text is scrolling
        if self.preset_scroller.needs_scrolling:
            wrap_x = preset_x + bbox_preset[2] - bbox_preset[0] + self.WRAP_GAP
            self.draw.text((wrap_x, preset_y), self.preset, 1, self.font)

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
            if event == 'press':
                self.held_count[ch] = 0
                if ch == touch.DOWN:
                    self.suppression.record()
                    self.api.set_preset_next()
                    self.update_display()
                elif ch == touch.UP:
                    self.suppression.record()
                    self.api.set_preset_prev()
                    self.update_display()
                elif ch == touch.LEFT:
                    self.suppression.record()
                    self.api.set_instrument_prev()
                    self.update_display()
                elif ch == touch.RIGHT:
                    self.suppression.record()
                    self.api.set_instrument_next()
                    self.update_display()

            elif event == 'held':
                if ch == touch.ENTER:
                    self.held_count[ch] = self.held_count.get(ch, 0) + 1
                    if self.held_count[ch] >= self.held_threshold:
                        self.on_enter_preset_menu()
                elif ch in (touch.UP, touch.DOWN, touch.LEFT, touch.RIGHT):
                    self.held_count[ch] = self.held_count.get(ch, 0) + 1
                    if self.held_count[ch] >= self.held_threshold:
                        if ch == touch.DOWN:
                            self.suppression.record()
                            self.api.set_preset_next()
                            self.update_display()
                        elif ch == touch.UP:
                            self.suppression.record()
                            self.api.set_preset_prev()
                            self.update_display()
                        elif ch == touch.LEFT:
                            self.suppression.record()
                            self.api.set_instrument_prev()
                            self.update_display()
                        elif ch == touch.RIGHT:
                            self.suppression.record()
                            self.api.set_instrument_next()
                            self.update_display()

            elif event == 'release':
                if ch == touch.ENTER:
                    if self.suppression.allow_action():
                        self.on_enter()
                elif ch in self.held_count:
                    del self.held_count[ch]

        return handler

    def get_image(self):
        return self.image

    def update_display(self):
        """Update display when instrument/preset changes (e.g., button press)."""
        current_instrument = self.api.get_current_instrument()
        self.preset = self.api.get_current_preset().display_name
        self.instrument = current_instrument.name
        self.background_primary = current_instrument.background_primary
        self.background_secondary = current_instrument.background_secondary
        # Update text and restart scrolling threads
        self.preset_scroller.update_text(self.preset)
        self.instrument_scroller.update_text(self.instrument)
        self.preset_scroller.start()
        self.instrument_scroller.start()
        self.draw_text()
        self.set_backlight()

    def start_scrolling(self):
        self.preset_scroller.start()
        self.instrument_scroller.start()

    def stop_scrolling(self):
        self.preset_scroller.stop()
        self.instrument_scroller.stop()
