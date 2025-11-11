from typing import Optional
import re


def find_longest_common_word_prefix(names: list[str]) -> str:
    """
    Find the longest common whole word prefix from a list of preset names.

    Words are separated by spaces, hyphens, and other common separators.
    Returns the common prefix as a string.

    Args:
        names: List of preset names

    Returns:
        The longest common word prefix (may be empty string)

    Examples:
        ["W1 roomy", "W1 Logical", "W1 - bright"] → "W1"
        ["Steel Drum", "Steel Drum natural"] → "Steel Drum"
        ["Hand Pan - foo", "Hand Pan bar"] → "Hand Pan"
        ["Foo", "Bar"] → ""
    """
    if not names:
        return ""

    if len(names) == 1:
        # For a single preset, use the full name as prefix
        # (will result in "Default" display name)
        return names[0]

    # Tokenize each name into words (split on spaces and separators)
    separator_pattern = r'[\s\-—:|\u2013\u2014]+'

    tokenized = []
    for name in names:
        # Split and filter out empty strings
        words = [w for w in re.split(separator_pattern, name) if w]
        tokenized.append(words)

    # Handle edge case where splitting resulted in empty word lists
    if not all(tokenized):
        return ""

    # Find the common prefix of word lists (case-insensitive comparison)
    common_words = []
    for i in range(min(len(words) for words in tokenized)):
        first_word = tokenized[0][i]
        if all(len(words) > i and words[i].lower() == first_word.lower()
               for words in tokenized):
            common_words.append(first_word)
        else:
            break

    # Join the common words back into a prefix string
    return ' '.join(common_words)


def calculate_display_name(preset_name: str, common_prefix: str) -> str:
    """
    Calculate the display name for a preset given the common prefix.

    Strips the common prefix and any following separators, then capitalizes.
    If the result would be empty or the name equals the prefix, returns "Default".

    Args:
        preset_name: The full preset name
        common_prefix: The common prefix to strip

    Returns:
        The display name suitable for showing in menus

    Examples:
        ("W1 roomy", "W1") → "Roomy"
        ("W1 - bright", "W1") → "Bright"
        ("W1", "W1") → "Default"
        ("Steel Drum natural", "Steel Drum") → "Natural"
    """
    if not common_prefix:
        # No common prefix, capitalize the full name
        return preset_name[0].upper() + preset_name[1:] if len(preset_name) > 1 else preset_name.upper()

    # Case-insensitive check if name starts with prefix
    if not preset_name.lower().startswith(common_prefix.lower()):
        return preset_name

    # Strip the prefix
    result = preset_name[len(common_prefix):]

    # Strip common separators and whitespace from the start
    result = re.sub(r'^[\s\-—:|\u2013\u2014]+', '', result).strip()

    # If nothing remains or name equals prefix, use "Default"
    if not result or preset_name.strip().lower() == common_prefix.strip().lower():
        return "Default"

    # Capitalize first letter
    return result[0].upper() + result[1:] if len(result) > 1 else result.upper()


class Preset:
    def __init__(self, name: str, display_name: Optional[str] = None):
        """
        Create a Preset instance.

        Args:
            name: The full preset name from Pianoteq API
            display_name: The formatted name for display (computed during library construction)
        """
        self.name = name
        self.display_name = display_name or name
        self.midi_program_number: Optional[int] = None
        self.midi_channel: Optional[int] = None

    def has_midi_params(self) -> bool:
        return self.midi_program_number is not None and \
               self.midi_channel is not None
