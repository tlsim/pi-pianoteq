from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.backlight import Backlight
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay
from gfxhat import touch


class InstrumentMenuDisplay(MenuDisplay):
    def __init__(self, api: ClientApi, width, height, font, on_exit, on_enter_preset_menu):
        super().__init__(api, width, height, font, on_exit)
        self.on_enter_preset_menu = on_enter_preset_menu
        self.instrument_selected = False

    def get_menu_options(self):
        instruments = self.api.get_instruments()
        menu_options = [MenuOption(i.name, self.set_instrument, self.font, (i.name,)) for i in instruments]
        return menu_options

    def get_heading(self):
        return "Select Instrument:"

    def set_instrument(self, name):
        self.api.set_instrument(name)
        self.instrument_selected = True
        self.on_exit()

    def update_instrument(self):
        current_instrument = self.api.get_current_instrument()
        current_option = next((o for o in self.menu_options if o.name == current_instrument.name), None)
        if current_option is not None:
            self.current_menu_option = self.menu_options.index(current_option)
            self._update_selected_option()
            self.draw_image()

    def get_handler(self):
        base_handler = super().get_handler()

        def handler(ch, event):
            if event == 'held':
                if ch == touch.ENTER:
                    self.held_count[ch] = self.held_count.get(ch, 0) + 1
                    if self.held_count[ch] >= self.held_threshold:
                        option_name = self.menu_options[self.current_menu_option].name
                        self.on_enter_preset_menu(option_name)
                    return

            base_handler(ch, event)

        return handler
