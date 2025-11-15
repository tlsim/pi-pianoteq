from PIL import Image, ImageDraw

from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.scrolling_text import ScrollingText
from pi_pianoteq.util.button_suppression import ButtonSuppression

from gfxhat import touch


class MenuDisplay:
    """
    Base class for menu displays with scrolling text for long option names.

    Uses a single ScrollingText instance for the currently selected option.
    Text is updated (reusing same instance) when user navigates menu.
    Threads are started when this display is visible, stopped when exiting menu.
    """
    MENU_ARROW_WIDTH = 10
    MENU_TEXT_MARGIN = 5
    MENU_ITEM_HEIGHT = 12
    WRAP_GAP = 20

    def __init__(self, api, width, height, font, on_exit):
        self.api = api
        self.width = width
        self.height = height
        self.font = font
        self.on_exit = on_exit
        self.suppression = ButtonSuppression(300)
        self.held_count = {}
        self.held_threshold = 2
        self.image = Image.new('P', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.menu_options = self.get_menu_options()
        self.backlight = Backlight("#cccccc")
        self.current_menu_option = 0
        self.selected_menu_option = 0
        self.option_scroller = None
        if self.menu_options:
            # Available width = total - arrow width - right margin
            menu_text_width = self.width - self.MENU_ARROW_WIDTH - self.MENU_TEXT_MARGIN
            self.option_scroller = ScrollingText(
                self.menu_options[0].name,
                self.font,
                max_width=menu_text_width
            )

        self.draw_image()

    def get_menu_options(self):
        raise NotImplementedError

    def get_heading(self):
        """Return heading text to display at top of menu (scrolls with menu items)."""
        raise NotImplementedError

    def get_backlight(self):
        return self.backlight

    def draw_image(self):
        """
        Render menu with scrolling for selected option.

        Uses seamless marquee: draws selected text twice when scrolling.
        Only scrolls text that genuinely doesn't fit in available width.
        """
        self.image.paste(0, (0, 0, self.width, self.height))
        offset_top = 0

        # Calculate vertical offset to center selected option
        for index in range(len(self.menu_options)):
            if index == self.current_menu_option:
                break
            offset_top += self.MENU_ITEM_HEIGHT

        # Get current scroll offset from background thread
        scroll_offset = self.option_scroller.get_offset() if self.option_scroller else 0

        # Draw heading at top of display (scrolls with menu items)
        heading = self.get_heading()
        if heading:
            heading_x = self.MENU_ARROW_WIDTH
            heading_y = 2 - offset_top
            self.draw.text((heading_x, heading_y), heading, 1, self.font)

        for index in range(len(self.menu_options)):
            x = self.MENU_ARROW_WIDTH
            y = (index * self.MENU_ITEM_HEIGHT) + (self.height / 2) - 4 - offset_top
            option = self.menu_options[index]
            if index == self.current_menu_option:
                self.draw.rectangle(((x-2, y-1), (self.width, y+10)), 1)

            is_selected = index == self.current_menu_option
            # Apply scroll offset only to selected option
            text_x = x if not is_selected else (x - scroll_offset)
            color = 0 if is_selected else 1
            self.draw.text((text_x, y), option.name, color, self.font)

            # Draw second copy for seamless wrap if scrolling has started
            # Check scroll_offset > 0 to avoid doubled text before scrolling begins
            # Check wrap_x < width to only draw when wrap is entering visible area
            if is_selected and self.option_scroller and self.option_scroller.needs_scrolling and scroll_offset > 0:
                option_bbox = self.font.getbbox(option.name)
                option_width = option_bbox[2] - option_bbox[0]
                wrap_x = text_x + option_width + self.WRAP_GAP
                if wrap_x < self.width:
                    self.draw.text((wrap_x, y), option.name, color, self.font)

        bbox = self.font.getbbox('>')
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        self.draw.text((0, (self.height - h) / 2), '>', 1, self.font)

    def get_handler(self):
        def handler(ch, event):
            if event == 'press':
                if ch == touch.BACK:
                    self.current_menu_option = self.selected_menu_option
                    self.on_exit()
                    return

                self.held_count[ch] = 0
                prev_option = self.current_menu_option

                if ch == touch.UP:
                    self.suppression.record()
                    self.current_menu_option -= 1
                elif ch == touch.DOWN:
                    self.suppression.record()
                    self.current_menu_option += 1
                elif ch == touch.LEFT:
                    self.suppression.record()
                    self.current_menu_option -= 1
                elif ch == touch.RIGHT:
                    self.suppression.record()
                    self.current_menu_option += 1

                self.current_menu_option %= len(self.menu_options)

                if prev_option != self.current_menu_option:
                    self._update_selected_option()

                self.draw_image()

            elif event == 'held':
                if ch in (touch.UP, touch.DOWN, touch.LEFT, touch.RIGHT):
                    self.held_count[ch] = self.held_count.get(ch, 0) + 1
                    if self.held_count[ch] >= self.held_threshold:
                        prev_option = self.current_menu_option

                        if ch == touch.UP:
                            self.suppression.record()
                            self.current_menu_option -= 1
                        elif ch == touch.DOWN:
                            self.suppression.record()
                            self.current_menu_option += 1
                        elif ch == touch.LEFT:
                            self.suppression.record()
                            self.current_menu_option -= 1
                        elif ch == touch.RIGHT:
                            self.suppression.record()
                            self.current_menu_option += 1

                        self.current_menu_option %= len(self.menu_options)

                        if prev_option != self.current_menu_option:
                            self._update_selected_option()

                        self.draw_image()

            elif event == 'release':
                if ch == touch.ENTER:
                    if self.suppression.allow_action():
                        self.menu_options[self.current_menu_option].trigger()
                        self.selected_menu_option = self.current_menu_option
                elif ch in self.held_count:
                    del self.held_count[ch]

        return handler

    def _update_selected_option(self):
        """Update scrolling text when user navigates to different menu option."""
        if self.option_scroller:
            self.option_scroller.update_text(self.menu_options[self.current_menu_option].name)
            self.option_scroller.start()

    def start_scrolling(self):
        if self.option_scroller:
            self.option_scroller.start()

    def stop_scrolling(self):
        if self.option_scroller:
            self.option_scroller.stop()

    def get_image(self):
        return self.image
