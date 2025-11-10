from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.gfxhat.menu_option import MenuOption
from pi_pianoteq.client.gfxhat.menu_display import MenuDisplay


class ShutdownDisplay(MenuDisplay):
    def __init__(self, api: ClientApi, width, height, font, on_exit):
        super().__init__(api, width, height, font, on_exit)
        self.backlight.set_all_backlights('#ddcccc')

    def get_menu_options(self):
        shutdown_option = MenuOption("OK", self.shutdown_device, self.font)
        cancel_option = MenuOption("Cancel", self.on_exit, self.font)
        return [shutdown_option, cancel_option]

    def get_heading(self):
        return "Shut down?"

    def shutdown_device(self):
        self.api.shutdown_device();
