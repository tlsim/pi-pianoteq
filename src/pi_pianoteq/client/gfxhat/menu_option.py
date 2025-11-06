class MenuOption:
    def __init__(self, name, action, font, options=()):
        self.name = name
        self.action = action
        self.options = options
        bbox = font.getbbox(name)
        self.width = bbox[2] - bbox[0]
        self.height = bbox[3] - bbox[1]
        self.size = (self.width, self.height)

    def trigger(self):
        self.action(*self.options)
