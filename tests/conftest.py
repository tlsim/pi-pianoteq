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

# Mock PIL.ImageFont.truetype to avoid loading real fonts
try:
    from PIL import ImageFont
    mock_font = mock.Mock()
    mock_font.getbbox = mock.Mock(return_value=(0, 0, 50, 10))
    ImageFont.truetype = mock.Mock(return_value=mock_font)
except ImportError:
    pass
