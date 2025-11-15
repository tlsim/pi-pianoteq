"""Type definitions for Pianoteq JSON-RPC API responses.

These types correspond to the Pianoteq JSON-RPC API documented in docs/pianoteq-api.md.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PresetInfo:
    """Full preset information from getListOfPresets().

    Corresponds to the PresetInfo interface in the API documentation.
    """
    name: str
    instr: str
    instrument_class: str
    collection: str
    license: str
    license_status: str  # "ok" or "demo"
    author: str
    bank: str
    comment: str
    file: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'PresetInfo':
        """Create PresetInfo from API response dict."""
        # Map 'class' to 'instrument_class'
        data_copy = data.copy()
        if 'class' in data_copy:
            data_copy['instrument_class'] = data_copy.pop('class')
        return cls(**data_copy)


@dataclass
class MiniPresetInfo:
    """Mini-preset information from getListOfPresets(preset_type=...).

    Used for velocity, mic, equalizer, reverb, tuning, and effect presets.
    """
    name: str
    author: str
    bank: str
    comment: str
    file: str


@dataclass
class CurrentPreset:
    """Current preset information (nested in PianoteqInfo)."""
    name: str = ""
    instrument: str = ""
    author: str = ""
    bank: str = ""
    comment: str = ""
    mini_presets: Dict[str, str] = field(default_factory=dict)


@dataclass
class PianoteqInfo:
    """Pianoteq state information from getInfo().

    Corresponds to the PianoteqInfo interface in the API documentation.
    """
    version: str = ""
    product_name: str = ""
    vendor_name: str = ""
    plugin_type: str = ""
    arch: str = ""
    arch_bits: int = 0
    build_date: str = ""
    modified: bool = False
    computing_parameter_update: bool = False
    current_preset: CurrentPreset = field(default_factory=CurrentPreset)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PianoteqInfo':
        """Create PianoteqInfo from API response dict."""
        data_copy = data.copy()
        # Convert nested current_preset dict to CurrentPreset object
        if 'current_preset' in data_copy and isinstance(data_copy['current_preset'], dict):
            data_copy['current_preset'] = CurrentPreset(**data_copy['current_preset'])
        return cls(**data_copy)


@dataclass
class ActivationInfo:
    """License and activation information from getActivationInfo().

    Corresponds to the ActivationInfo interface in the API documentation.
    """
    error_msg: str = "Demo"  # "Demo" for trial, "" for licensed
    addons: list = field(default_factory=list)
    # Licensed-only fields (optional)
    name: Optional[str] = None
    email: Optional[str] = None
    hwname: Optional[str] = None
    status: Optional[int] = None
