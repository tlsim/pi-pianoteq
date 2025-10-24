from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Box, Frame, TextArea

from pi_pianoteq.client.Client import Client
from pi_pianoteq.client.ClientApi import ClientApi


class CliClient(Client):
    def __init__(self, api: ClientApi):
        super().__init__(api)

        self.text_area = TextArea(
            text='Hello world!\nPress control-c to quit.',
            width=60,
            height=20,
            read_only=True,
            focusable=False,
        )
        root_container = Box(Frame(self.text_area))
        layout = Layout(container=root_container)

        # Key bindings.
        kb = KeyBindings()

        @kb.add('c-c')
        def kb_exit(event):
            event.app.exit()

        @kb.add('c-k')
        def kb_get_current(event):
            self.text_area.text = f'Current Preset: {self.api.get_current_preset_display_name()}'

        @kb.add('c-n')
        def kb_preset_next(event):
            self.api.set_preset_next()
            self.text_area.text = f'Current Preset: {self.api.get_current_preset_display_name()}'

        @kb.add('c-p')
        def kb_preset_prev(event):
            self.api.set_preset_prev()
            self.text_area.text = f'Current Preset: {self.api.get_current_preset_display_name()}'

        # Build a main application object.
        self.application = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=True)

    def start(self):
        self.application.run()
