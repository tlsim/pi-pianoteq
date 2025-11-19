import unittest
from unittest.mock import Mock

from pi_pianoteq.client.gfxhat.control_menu_display import ControlMenuDisplay


class ControlMenuDisplayTestCase(unittest.TestCase):
    """Test ControlMenuDisplay menu options and callbacks."""

    def setUp(self):
        """Set up common mocks for tests."""
        self.mock_api = Mock()
        self.mock_font = Mock()
        self.mock_font.getbbox.return_value = (0, 0, 50, 10)
        self.on_exit = Mock()
        self.on_select_instrument = Mock()
        self.on_randomize_preset = Mock()
        self.on_random_instrument = Mock()

    def create_display(self):
        """Helper to create ControlMenuDisplay with mocks."""
        return ControlMenuDisplay(
            api=self.mock_api,
            width=128,
            height=64,
            font=self.mock_font,
            on_exit=self.on_exit,
            on_select_instrument=self.on_select_instrument,
            on_randomize_preset=self.on_randomize_preset,
            on_random_instrument=self.on_random_instrument
        )

    def test_get_menu_options_includes_all_options(self):
        """Menu options should include instrument selection and randomization options."""
        display = self.create_display()

        self.assertEqual(len(display.menu_options), 3)
        self.assertEqual(display.menu_options[0].name, "Select Instrument")
        self.assertEqual(display.menu_options[1].name, "Randomize Preset")
        self.assertEqual(display.menu_options[2].name, "Random Instrument")

    def test_select_instrument_triggers_callback(self):
        """Selecting 'Select Instrument' should trigger callback."""
        display = self.create_display()

        display.menu_options[0].trigger()

        self.on_select_instrument.assert_called_once()

    def test_randomize_preset_triggers_callback(self):
        """Selecting 'Randomize Preset' should trigger callback."""
        display = self.create_display()

        display.menu_options[1].trigger()

        self.on_randomize_preset.assert_called_once()

    def test_random_instrument_triggers_callback(self):
        """Selecting 'Random Instrument' should trigger callback."""
        display = self.create_display()

        display.menu_options[2].trigger()

        self.on_random_instrument.assert_called_once()

    def test_get_heading_returns_menu_title(self):
        """get_heading should return 'Menu:'."""
        display = self.create_display()

        self.assertEqual(display.get_heading(), "Menu:")


if __name__ == '__main__':
    unittest.main()
