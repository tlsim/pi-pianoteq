from PIL import Image, ImageDraw

from pi_pianoteq.client.gfxhat.Backlight import Backlight


class LoadingDisplay:
    """
    Simple loading display for GFX HAT showing centered message with blue backlight.

    Follows the same pattern as InstrumentDisplay/InstrumentMenuDisplay for consistency.
    """

    LOADING_BACKLIGHT_COLOR = '#1e3a5f'  # Calming blue

    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        self.message = ""
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.backlight = Backlight(self.LOADING_BACKLIGHT_COLOR)

    def set_message(self, message: str):
        """Update the loading message and redraw"""
        self.message = message
        self.draw_image()

    def draw_image(self):
        """Draw centered loading message"""
        # Clear display
        self.image.paste(0, (0, 0, self.width, self.height))

        # Draw centered text
        bbox = self.font.getbbox(self.message)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        self.draw.text((x, y), self.message, 1, self.font)

    def get_image(self):
        return self.image

    def get_backlight(self):
        return self.backlight
