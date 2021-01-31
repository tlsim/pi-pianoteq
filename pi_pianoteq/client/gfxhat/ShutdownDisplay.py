from pi_pianoteq.client.ClientApi import ClientApi
from pi_pianoteq.client.gfxhat.MenuOption import MenuOption
from pi_pianoteq.client.gfxhat.MenuDisplay import MenuDisplay


class ShutdownDisplay(MenuDisplay):
    def __init__(self, api: ClientApi, width, height, font, on_exit):
        super().__init__(api, width, height, font, on_exit)
        self.backlight.set_all_backlights('#ddcccc')

    def get_menu_options(self):
        shutdown_option = MenuOption("OK", self.shutdown_device, self.font)
        cancel_option = MenuOption("Cancel", self.on_exit, self.font)
        return [shutdown_option, cancel_option]

    def shutdown_device(self):
        self.api.shutdown_device();
