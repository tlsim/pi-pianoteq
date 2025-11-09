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

# Mock PIL.ImageFont.truetype to avoid loading real fonts
from PIL import ImageFont
mock_font = mock.Mock()
mock_font.getbbox = mock.Mock(return_value=(0, 0, 50, 10))
ImageFont.truetype = mock.Mock(return_value=mock_font)

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
