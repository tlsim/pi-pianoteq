from gfxhat import backlight


class Backlight:

    def __init__(self, hex_colour):
        self.backlights = [0 for x in range(18)]
        self.set_all_backlights(hex_colour)

    @staticmethod
    def hex_to_rgb(hex_colour):
        h = hex_colour.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def set_all_backlights(self, hex_colour):
        for i in range(6):
            self.set_backlight(hex_colour, i)

    def set_backlight(self, hex_colour, backlight_index):
        r, g, b = self.hex_to_rgb(hex_colour)
        i = backlight_index
        self.backlights[(i * 3):(i * 3) + 3] = r, g, b

    def apply_backlight(self):
        for i in range(6):
            r, g, b = self.backlights[(i * 3): (i * 3) + 3]
            backlight.set_pixel(i, r, g, b)
