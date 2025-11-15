"""Utilities for processing preset names and calculating display names."""

import re


def find_longest_common_word_prefix(names: list[str]) -> str:
    """
    Find the longest common whole word prefix from a list of preset names.

    Compares words case-insensitively, separated by spaces, hyphens, colons, etc.
    Returns empty string if no common prefix exists.

    Examples:
        ["W1 roomy", "W1 Logical", "W1 - bright"] -> "W1"
        ["Piano Classic", "Piano Modern"] -> "Piano"
        ["Harp", "Guitar"] -> ""
    """
    if not names or len(names) == 1:
        return names[0] if names else ""

    separator_pattern = r'[\s\-—:|\u2013\u2014]+'

    tokenized = [re.split(separator_pattern, name.strip()) for name in names]

    common_prefix = []
    for i in range(min(len(tokens) for tokens in tokenized)):
        words_at_position = [tokens[i].lower() for tokens in tokenized]
        if len(set(words_at_position)) == 1:
            common_prefix.append(tokenized[0][i])
        else:
            break

    return ' '.join(common_prefix)


def calculate_display_name(preset_name: str, common_prefix: str) -> str:
    """
    Calculate a display name by removing the common prefix and capitalizing.

    Returns "Default" if the preset name equals the prefix.

    Examples:
        ("W1 roomy", "W1") -> "Roomy"
        ("W1", "W1") -> "Default"
        ("Piano", "") -> "Piano"
    """
    if not common_prefix:
        return preset_name[0].upper() + preset_name[1:] if len(preset_name) > 1 else preset_name.upper()

    separator_pattern = r'[\s\-—:|\u2013\u2014]+'

    # Tokenize both the preset name and prefix
    preset_tokens = re.split(separator_pattern, preset_name.strip())
    prefix_tokens = re.split(separator_pattern, common_prefix.strip())

    # Check if preset starts with prefix (case-insensitive token comparison)
    if len(preset_tokens) < len(prefix_tokens):
        return preset_name

    for i, prefix_token in enumerate(prefix_tokens):
        if preset_tokens[i].lower() != prefix_token.lower():
            return preset_name

    # If name equals prefix, return "Default"
    if len(preset_tokens) == len(prefix_tokens):
        return "Default"

    # Join the remaining tokens with spaces
    result_tokens = preset_tokens[len(prefix_tokens):]
    result = ' '.join(result_tokens)

    # Capitalize first letter
    return result[0].upper() + result[1:] if len(result) > 1 else result.upper()
