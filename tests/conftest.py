"""
Pytest configuration to mock hardware dependencies.

This must run before any test modules are imported to prevent
hardware library imports from failing in CI environments.
"""
import sys
from types import ModuleType
from unittest import mock

# Mock gfxhat modules before any test imports
gfxhat = ModuleType('gfxhat')
gfxhat.lcd = ModuleType('lcd')
gfxhat.touch = ModuleType('touch')
gfxhat.backlight = ModuleType('backlight')
gfxhat.fonts = ModuleType('fonts')

# Add to sys.modules
sys.modules['gfxhat'] = gfxhat
sys.modules['gfxhat.lcd'] = gfxhat.lcd
sys.modules['gfxhat.touch'] = gfxhat.touch
sys.modules['gfxhat.backlight'] = gfxhat.backlight
sys.modules['gfxhat.fonts'] = gfxhat.fonts

# Set up touch button constants
gfxhat.touch.ENTER = 0
gfxhat.touch.BACK = 1
gfxhat.touch.UP = 2
gfxhat.touch.DOWN = 3
gfxhat.touch.LEFT = 4
gfxhat.touch.RIGHT = 5

# Set up fonts path
gfxhat.fonts.BitbuntuFull = "/fake/font.ttf"

# Mock LCD dimensions
gfxhat.lcd.dimensions = mock.Mock(return_value=(128, 64))

# Mock PIL to avoid real image operations
try:
    from PIL import ImageFont, Image, ImageDraw

    # Mock font
    mock_font = mock.Mock()
    mock_font.getbbox = mock.Mock(return_value=(0, 0, 50, 10))
    mock_font.getmask2 = mock.Mock(return_value=(mock.Mock(), (0, 0)))
    ImageFont.truetype = mock.Mock(return_value=mock_font)

    # Mock Image.new to return a mock image
    original_image_new = Image.new
    def mock_image_new(mode, size, color=0):
        mock_img = mock.Mock()
        mock_img.mode = mode
        mock_img.size = size
        return mock_img
    Image.new = mock_image_new

    # Mock ImageDraw.Draw to return a mock draw object
    original_draw = ImageDraw.Draw
    def mock_draw(image, mode=None):
        mock_drawer = mock.Mock()
        mock_drawer.text = mock.Mock()
        mock_drawer.rectangle = mock.Mock()
        mock_drawer.line = mock.Mock()
        return mock_drawer
    ImageDraw.Draw = mock_draw
except ImportError:
    pass
