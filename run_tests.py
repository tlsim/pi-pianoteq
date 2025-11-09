#!/usr/bin/env python3
"""Test runner that mocks hardware dependencies."""

import sys
from types import ModuleType
from unittest import mock

# Mock gfxhat modules before any imports
gfxhat = ModuleType('gfxhat')
gfxhat.lcd = ModuleType('lcd')
gfxhat.touch = ModuleType('touch')
gfxhat.backlight = ModuleType('backlight')
gfxhat.fonts = ModuleType('fonts')

# Add mocked modules to sys.modules
sys.modules['gfxhat'] = gfxhat
sys.modules['gfxhat.lcd'] = gfxhat.lcd
sys.modules['gfxhat.touch'] = gfxhat.touch
sys.modules['gfxhat.backlight'] = gfxhat.backlight
sys.modules['gfxhat.fonts'] = gfxhat.fonts

# Set up some basic attributes
gfxhat.touch.ENTER = 0
gfxhat.touch.BACK = 1
gfxhat.touch.UP = 2
gfxhat.touch.DOWN = 3
gfxhat.touch.LEFT = 4
gfxhat.touch.RIGHT = 5
gfxhat.fonts.BitbuntuFull = "/fake/font.ttf"

# Mock PIL to avoid real image operations
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

# Now we can run tests
import unittest

if __name__ == '__main__':
    # Add src to path
    sys.path.insert(0, 'src')

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
