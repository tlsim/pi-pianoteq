# CLI Client Refactoring Opportunities

This document outlines potential refactoring opportunities for the CLI client to improve modularity and maintainability. The current implementation is functional and well-tested (49 tests, all passing), but could benefit from extracting some concerns into separate classes.

## Current State

The `CliClient` class has grown to ~730 lines with the addition of:
- Preset menu functionality
- Search functionality (instrument, preset, combined)
- Multiple display modes

**Strengths:**
- Well-structured state machine
- Comprehensive test coverage
- Clear separation of concerns in methods

**Areas for improvement:**
- Search logic could be extracted
- Display text generation methods are quite long
- State management is spread across multiple boolean flags

## Refactoring Option 1: Extract Search Manager

**Complexity:** Low
**Benefit:** High
**Recommended:** Yes

Extract search functionality into a dedicated class:

```python
class SearchManager:
    """Manages search state and filtering for CLI client."""

    def __init__(self, api: ClientApi):
        self.api = api
        self.query = ""
        self.context = None  # 'instrument', 'preset', 'combined'
        self.filtered_items = []

    def enter_search(self, context: str, preset_menu_instrument: str = None):
        """Enter search mode with given context."""

    def update_results(self):
        """Filter items based on current query."""

    def select_result(self, index: int) -> tuple:
        """Return (action_type, action_data) for selected result."""
```

**Benefits:**
- Isolates search logic for easier testing
- Reduces CliClient complexity
- Makes search logic reusable

**Implementation:**
1. Create `src/pi_pianoteq/client/cli/search_manager.py`
2. Move search methods from CliClient
3. Update CliClient to use SearchManager
4. Add dedicated tests for SearchManager

## Refactoring Option 2: Extract Display Renderer

**Complexity:** Medium
**Benefit:** Medium
**Recommended:** Consider if adding more display modes

Create a renderer class for generating formatted text:

```python
class CliDisplayRenderer:
    """Generates formatted text for different display modes."""

    def render_normal(self, instrument, preset) -> List[Tuple[str, str]]:
        """Render normal mode display."""

    def render_instrument_menu(self, items, selected_idx, scroll_offset, visible) -> List[Tuple[str, str]]:
        """Render instrument menu."""

    def render_preset_menu(self, presets, selected_idx, ...) -> List[Tuple[str, str]]:
        """Render preset menu."""

    def render_search(self, query, results, selected_idx, context, ...) -> List[Tuple[str, str]]:
        """Render search results."""
```

**Benefits:**
- Separates rendering logic from state management
- Easier to test display formatting
- Could enable themed displays in future

**Drawbacks:**
- More indirection
- May be over-engineering for current needs

## Refactoring Option 3: State Machine Pattern

**Complexity:** High
**Benefit:** Medium
**Recommended:** Only if adding many more states

Implement formal state machine pattern:

```python
class CliState(ABC):
    """Base class for CLI states."""

    @abstractmethod
    def handle_key(self, key: str) -> Optional['CliState']:
        """Handle key press, return new state if transitioning."""

    @abstractmethod
    def render(self) -> List[Tuple[str, str]]:
        """Render this state's display."""

class NormalState(CliState):
    """Normal display mode."""

class InstrumentMenuState(CliState):
    """Instrument menu mode."""

class SearchState(CliState):
    """Search mode."""
```

**Benefits:**
- Clean separation of state-specific behavior
- Easier to add new states
- More testable in isolation

**Drawbacks:**
- Significant refactoring effort
- May be overkill for 4 states
- More complex mental model

## Refactoring Option 4: Menu Navigator

**Complexity:** Low
**Benefit:** Low
**Recommended:** No

Extract menu navigation logic:

```python
class MenuNavigator:
    """Handles menu navigation and scrolling."""

    def __init__(self, visible_items: int = 10):
        self.visible_items = visible_items

    def next(self, current: int, total: int) -> int:
        """Get next index."""

    def prev(self, current: int) -> int:
        """Get previous index."""

    def scroll_offset(self, current: int, total: int) -> int:
        """Calculate scroll offset."""
```

**Benefits:**
- Reusable navigation logic
- Easier to test scrolling calculations

**Drawbacks:**
- Navigation logic is already simple
- Adds another class for minimal benefit
- Current implementation is clear

## Recommendation Summary

**Recommended now:**
1. **Extract SearchManager** (Option 1) - High value, low complexity

**Consider later:**
2. **Extract CliDisplayRenderer** (Option 2) - If adding more display modes or themes

**Not recommended:**
3. **State Machine Pattern** (Option 3) - Over-engineering for current needs
4. **Menu Navigator** (Option 4) - No significant benefit

## Implementation Priority

If refactoring is desired:

### Phase 1: Search Manager (1-2 hours)
- Create SearchManager class
- Move search methods
- Update tests to test SearchManager independently
- Update CliClient to use SearchManager

### Phase 2: Consider Display Renderer (2-3 hours, optional)
- Only if adding more display features
- Create CliDisplayRenderer
- Move display methods
- Add renderer tests

## Code Quality Metrics

Current state (after adding tests):
- **Lines of code:** ~730
- **Test coverage:** Comprehensive (49 tests)
- **Complexity:** Moderate (manageable with current structure)
- **Maintainability:** Good (clear method names, well-documented)

After SearchManager extraction:
- **CliClient lines:** ~550 (25% reduction)
- **SearchManager lines:** ~180
- **Test coverage:** Same or better
- **Complexity:** Lower in CliClient
- **Maintainability:** Better (clear separation of concerns)

## Conclusion

The current implementation is well-structured and doesn't urgently need refactoring. However, extracting SearchManager (Option 1) would provide clear benefits with minimal effort. Other refactorings should be considered only if adding significant new functionality.

The comprehensive test suite (49 tests) provides confidence that any refactoring can be done safely with immediate feedback on regressions.
