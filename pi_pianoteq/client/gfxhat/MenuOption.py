class MenuOption:
    def __init__(self, name, action, font, options=()):
        self.name = name
        self.action = action
        self.options = options
        self.size = font.getsize(name)
        self.width, self.height = self.size

    def trigger(self):
        self.action(*self.options)
