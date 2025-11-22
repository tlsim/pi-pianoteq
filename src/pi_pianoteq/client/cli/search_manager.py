from typing import List, Tuple, Optional
from pi_pianoteq.client.client_api import ClientApi


class SearchManager:
    """
    Manages search state and filtering for CLI client.

    Supports three search contexts:
    - 'instrument': Search instruments only
    - 'preset': Search presets for a specific instrument
    - 'combined': Search both instruments and presets

    Filtered items are stored as tuples: (display_name, item_type, data)
    where item_type is 'instrument' or 'preset', and data contains the
    information needed to load that item.
    """

    def __init__(self, api: ClientApi):
        self.api = api
        self.query = ""
        self.context = None
        self.filtered_items: List[Tuple[str, str, any]] = []
        self.preset_menu_instrument = None

    def enter_search(self, context: str, preset_menu_instrument: Optional[str] = None):
        """
        Enter search mode with given context.

        Args:
            context: One of 'instrument', 'preset', 'combined'
            preset_menu_instrument: Required if context is 'preset'
        """
        self.context = context
        self.query = ""
        self.preset_menu_instrument = preset_menu_instrument
        self.update_results()

    def exit_search(self):
        """Exit search mode and reset state."""
        self.query = ""
        self.context = None
        self.filtered_items = []
        self.preset_menu_instrument = None

    def set_query(self, query: str):
        """Update search query and refresh results."""
        self.query = query
        self.update_results()

    def update_results(self):
        """Update filtered items based on current query and context."""
        query_lower = self.query.lower()

        if self.context == 'instrument':
            # Search instruments only
            instruments = self.api.get_instruments()
            all_items = [(instr.name, 'instrument', instr.name) for instr in instruments]

        elif self.context == 'preset':
            # Search presets only (for current preset menu instrument)
            if not self.preset_menu_instrument:
                self.filtered_items = []
                return

            presets = self.api.get_presets(self.preset_menu_instrument)
            all_items = [(p.get_display_name_with_modified(), 'preset', p.name) for p in presets]

        else:  # combined
            # Search both instruments and presets
            all_items = []

            # Add instruments
            for instrument in self.api.get_instruments():
                all_items.append((instrument.name, 'instrument', instrument.name))

            # Add presets from all instruments
            for instrument in self.api.get_instruments():
                for preset in instrument.presets:
                    display = f"{preset.get_display_name_with_modified()} ({instrument.name})"
                    all_items.append((display, 'preset', (instrument.name, preset.name)))

        # Filter items by query
        if query_lower:
            self.filtered_items = [
                item for item in all_items
                if query_lower in item[0].lower()
            ]
        else:
            self.filtered_items = all_items

    def get_selection_action(self, index: int) -> Optional[Tuple[str, any]]:
        """
        Get the action to perform for the selected search result.

        Args:
            index: Index of selected item in filtered_items

        Returns:
            Tuple of (action_type, action_data) or None if invalid index
            - For instruments: ('set_instrument', instrument_name)
            - For presets in combined search: ('set_preset', (instrument_name, preset_name))
            - For presets in preset search: ('set_preset_single', preset_name)
        """
        if not self.filtered_items or index >= len(self.filtered_items):
            return None

        display_name, item_type, data = self.filtered_items[index]

        if item_type == 'instrument':
            return ('set_instrument', data)
        else:  # preset
            if self.context == 'combined':
                # Combined search: data is (instrument_name, preset_name)
                return ('set_preset', data)
            else:
                # Preset-only search: data is just preset_name
                return ('set_preset_single', data)

    def has_results(self) -> bool:
        """Check if there are any search results."""
        return len(self.filtered_items) > 0

    def result_count(self) -> int:
        """Get the number of search results."""
        return len(self.filtered_items)

    def is_active(self) -> bool:
        """Check if search mode is currently active."""
        return self.context is not None
