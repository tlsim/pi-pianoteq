"""Display text generation for CLI client."""

import os
from typing import List, Tuple

from pi_pianoteq.client.client_api import ClientApi
from pi_pianoteq.client.cli.search_manager import SearchManager
from pi_pianoteq.logging.logging_config import BufferedLoggingHandler


def calculate_menu_visible_items() -> int:
    """Calculate how many menu items can fit based on terminal height"""
    try:
        terminal_height = os.get_terminal_size().lines
    except (OSError, AttributeError):
        return 10  # Default if can't detect terminal size

    # Account for UI elements:
    # - Frame top/bottom: 2 lines
    # - Title: 1 line
    # - Header newline: 1 line
    # - Scroll indicator (top): 1 line
    # - Scroll indicator (bottom): 1 line
    # - Footer newline: 1 line
    # - Controls section: 6 lines (varies, but average)
    reserved_lines = 13

    available_lines = terminal_height - reserved_lines
    return max(5, available_lines)  # At least 5 items visible


def get_title(search_manager: SearchManager, preset_menu_mode: bool,
              preset_menu_instrument: str, menu_mode: bool, logs_view_mode: bool = False) -> str:
    """Get frame title based on current mode"""
    if logs_view_mode:
        return "View Logs"
    elif search_manager.is_active():
        if search_manager.context == 'instrument':
            return "Search Instruments"
        elif search_manager.context == 'preset':
            return f"Search Presets - {search_manager.preset_menu_instrument}"
        else:
            return "Search Instruments & Presets"
    elif preset_menu_mode:
        return f"Select Preset - {preset_menu_instrument}"
    elif menu_mode:
        return "Select Instrument"
    else:
        return "Pi-Pianoteq CLI"


def get_normal_text(api: ClientApi) -> List[Tuple[str, str]]:
    """Generate normal mode display using formatted text tuples"""
    instrument = api.get_current_instrument()
    preset = api.get_current_preset().display_name

    lines = [
        ('', '\n'),
        ('bold cyan', 'Instrument:'), ('', '\n'),
        ('ansigreen', f'  {instrument.name}'), ('', '\n'),
        ('', '\n'),
        ('bold cyan', 'Preset:'), ('', '\n'),
        ('ansiyellow', f'  {preset}'), ('', '\n'),
        ('', '\n'),
        ('bold underline', 'Controls:'), ('', '\n'),
        ('', '  Up/Down     : Navigate presets\n'),
        ('', '  Left/Right  : Quick instrument switch\n'),
        ('bold', '  i'), ('', '           : Open instrument menu\n'),
        ('bold', '  p'), ('', '           : Open preset menu\n'),
        ('bold', '  r'), ('', '           : Randomize current preset\n'),
        ('bold', '  R'), ('', '           : Random all (instrument + preset)\n'),
        ('bold', '  /'), ('', '           : Search instruments & presets\n'),
        ('bold', '  l'), ('', '           : View logs\n'),
        ('bold', '  q'), ('', '           : Quit\n'),
        ('', '\n'),
    ]

    return lines


def get_instrument_menu_text(instrument_names: List[str], current_menu_index: int,
                             menu_scroll_offset: int) -> List[Tuple[str, str]]:
    """Generate instrument menu display using formatted text tuples"""
    lines = [('', '\n')]

    # Calculate visible items based on current terminal size
    menu_visible_items = calculate_menu_visible_items()

    # Calculate visible range
    start_idx = menu_scroll_offset
    end_idx = min(start_idx + menu_visible_items, len(instrument_names))

    # Add scroll indicator if needed
    if start_idx > 0:
        lines.append(('ansigray', '  ... (Up for more)\n'))
    else:
        lines.append(('', '\n'))

    # Add visible menu items
    for i in range(start_idx, end_idx):
        instrument = instrument_names[i]
        # Truncate long names to fit in display
        display_name = instrument[:58] if len(instrument) > 58 else instrument

        if i == current_menu_index:
            # Highlight selected item
            lines.append(('bold cyan', f'  > {display_name}\n'))
        else:
            lines.append(('', f'    {display_name}\n'))

    # Fill remaining space if needed
    displayed_items = end_idx - start_idx
    if start_idx > 0:
        displayed_items += 1  # Account for "..." line

    for _ in range(menu_visible_items - displayed_items):
        lines.append(('', '\n'))

    # Add scroll indicator at bottom if needed
    if end_idx < len(instrument_names):
        lines.append(('ansigray', '  ... (Down for more)\n'))
    else:
        lines.append(('', '\n'))

    lines.extend([
        ('', '\n'),
        ('bold underline', 'Menu Controls:'), ('', '\n'),
        ('', '  Up/Down  : Navigate menu\n'),
        ('bold', '  Enter'), ('', '    : Select instrument\n'),
        ('bold', '  p'), ('', '        : View presets for selected instrument\n'),
        ('bold', '  /'), ('', '        : Search instruments\n'),
        ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Exit menu\n'),
        ('', '\n'),
    ])

    return lines


def get_preset_menu_text(api: ClientApi, preset_menu_instrument: str,
                         current_menu_index: int, menu_scroll_offset: int) -> List[Tuple[str, str]]:
    """Generate preset menu display using formatted text tuples"""
    lines = [('', '\n')]

    # Get presets with display names
    presets = api.get_presets(preset_menu_instrument)

    # Calculate visible items based on current terminal size
    menu_visible_items = calculate_menu_visible_items()

    # Calculate visible range
    start_idx = menu_scroll_offset
    end_idx = min(start_idx + menu_visible_items, len(presets))

    # Add scroll indicator if needed
    if start_idx > 0:
        lines.append(('ansigray', '  ... (Up for more)\n'))
    else:
        lines.append(('', '\n'))

    # Add visible menu items
    for i in range(start_idx, end_idx):
        preset = presets[i]
        # Truncate long names to fit in display
        display_name = preset.display_name[:58] if len(preset.display_name) > 58 else preset.display_name

        if i == current_menu_index:
            # Highlight selected item
            lines.append(('bold cyan', f'  > {display_name}\n'))
        else:
            lines.append(('', f'    {display_name}\n'))

    # Fill remaining space if needed
    displayed_items = end_idx - start_idx
    if start_idx > 0:
        displayed_items += 1  # Account for "..." line

    for _ in range(menu_visible_items - displayed_items):
        lines.append(('', '\n'))

    # Add scroll indicator at bottom if needed
    if end_idx < len(presets):
        lines.append(('ansigray', '  ... (Down for more)\n'))
    else:
        lines.append(('', '\n'))

    lines.extend([
        ('', '\n'),
        ('bold underline', 'Menu Controls:'), ('', '\n'),
        ('', '  Up/Down  : Navigate menu\n'),
        ('bold', '  Enter'), ('', '    : Select preset\n'),
        ('bold', '  /'), ('', '        : Search presets\n'),
        ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Exit menu\n'),
        ('', '\n'),
    ])

    return lines


def get_search_text(search_manager: SearchManager, current_menu_index: int,
                   menu_scroll_offset: int) -> List[Tuple[str, str]]:
    """Generate search mode display using formatted text tuples"""
    lines = [('', '\n')]

    # Show search query
    lines.extend([
        ('bold cyan', 'Search: '), ('ansiyellow', search_manager.query), ('', '\n'),
        ('', '\n'),
    ])

    # Show result count
    result_count = search_manager.result_count()
    if result_count == 0:
        lines.append(('ansigray', f'  No matches found\n'))
        lines.append(('', '\n'))
    else:
        lines.append(('ansigray', f'  {result_count} result(s)\n'))

    # Calculate visible items based on current terminal size
    menu_visible_items = calculate_menu_visible_items()

    # Calculate visible range
    start_idx = menu_scroll_offset
    end_idx = min(start_idx + menu_visible_items, len(search_manager.filtered_items))

    # Add scroll indicator if needed
    if start_idx > 0:
        lines.append(('ansigray', '  ... (Up for more)\n'))
    else:
        lines.append(('', '\n'))

    # Add visible search results
    for i in range(start_idx, end_idx):
        display_name, item_type, data = search_manager.filtered_items[i]
        # Truncate long names to fit in display
        display_text = display_name[:56] if len(display_name) > 56 else display_name

        # Add type indicator
        if search_manager.context == 'combined':
            type_indicator = '[I]' if item_type == 'instrument' else '[P]'
            display_text = f"{type_indicator} {display_text}"

        if i == current_menu_index:
            # Highlight selected item
            lines.append(('bold cyan', f'  > {display_text}\n'))
        else:
            lines.append(('', f'    {display_text}\n'))

    # Fill remaining space if needed
    displayed_items = end_idx - start_idx
    if start_idx > 0:
        displayed_items += 1  # Account for "..." line

    for _ in range(menu_visible_items - displayed_items):
        lines.append(('', '\n'))

    # Add scroll indicator at bottom if needed
    if end_idx < len(search_manager.filtered_items):
        lines.append(('ansigray', '  ... (Down for more)\n'))
    else:
        lines.append(('', '\n'))

    lines.extend([
        ('', '\n'),
        ('bold underline', 'Search Controls:'), ('', '\n'),
        ('', '  Type to search\n'),
        ('', '  Up/Down     : Navigate results\n'),
        ('bold', '  Enter'), ('', '       : Select item\n'),
        ('bold', '  Backspace'), ('', '   : Delete character (or exit if empty)\n'),
        ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', '    : Exit search\n'),
        ('', '\n'),
    ])

    return lines


def format_log_messages(log_buffer: BufferedLoggingHandler, reserved_lines: int = 10,
                        default_max_lines: int = 20) -> List[Tuple[str, str]]:
    """Format log messages for display with terminal-aware sizing"""
    messages = log_buffer.get_messages()

    if not messages:
        return [('ansigray', '  Initializing...\n')]

    # Calculate terminal dimensions
    try:
        terminal_size = os.get_terminal_size()
        terminal_height = terminal_size.lines
        terminal_width = terminal_size.columns
        max_log_lines = max(10, terminal_height - reserved_lines)
    except (OSError, AttributeError):
        max_log_lines = default_max_lines
        terminal_width = 80

    # Account for frame borders and padding
    max_line_width = terminal_width - 6

    # Build log lines
    lines = []
    visible_messages = messages[-max_log_lines:]
    for msg in visible_messages:
        # Truncate message if too long
        if len(msg) > max_line_width:
            truncated_msg = msg[:max_line_width - 3] + '...'
        else:
            truncated_msg = msg
        lines.append(('ansibrightblack', f'  {truncated_msg}\n'))

    return lines


def get_logs_view_text(log_buffer: BufferedLoggingHandler) -> List[Tuple[str, str]]:
    """Generate logs view display using formatted text tuples"""
    messages = log_buffer.get_messages()

    if not messages:
        return [
            ('', '\n'),
            ('ansigray', '  No logs available\n'),
            ('', '\n'),
        ]

    lines = [('', '\n')]
    lines.extend(format_log_messages(log_buffer, reserved_lines=10, default_max_lines=20))

    lines.extend([
        ('', '\n'),
        ('bold underline', 'Logs Controls:'), ('', '\n'),
        ('bold', '  Esc'), ('', ' or '), ('bold', 'q'), ('', ' : Return to main view\n'),
        ('', '\n'),
    ])

    return lines
