# MCP Server Improvements for Agentic Game Playing

## Current Implementation Analysis

### Strengths
- Clean tool interface via MCP protocol
- No dependency on screen position/resolution
- Programmatic control through Lua
- Reliable state reading

### Weaknesses
1. **Performance**: File-based polling with 0.5s delays
2. **State Representation**: Raw grid without semantic information
3. **Navigation**: Hardcoded for only levels 1-7
4. **Error Handling**: Limited feedback on failed actions
5. **Game Events**: No real-time win/loss detection
6. **Batching**: Commands executed one at a time

## Proposed Improvements

### 1. Enhanced State Representation

```python
@mcp.tool()
def get_semantic_state() -> dict:
    """Get structured game state with semantic analysis."""
    return {
        "grid": get_game_state(),  # Current ASCII grid
        "rules": [
            {"subject": "BABA", "verb": "IS", "property": "YOU"},
            {"subject": "WALL", "verb": "IS", "property": "STOP"},
            {"subject": "FLAG", "verb": "IS", "property": "WIN"}
        ],
        "controlled_entities": [{"type": "baba", "pos": [16, 12]}],
        "win_conditions": [{"type": "flag", "positions": [[12, 9]]}],
        "pushable_text": [
            {"text": "WALL", "pos": [10, 13]},
            {"text": "IS", "pos": [11, 13]}
        ],
        "obstacles": {
            "walls": [[10, 3], [11, 3], ...],
            "water": [],
            "lava": []
        }
    }
```

### 2. Event System

```python
@mcp.tool()
def subscribe_events() -> str:
    """Subscribe to game events (win, lose, rule_change)."""
    # Returns event stream ID
    
@mcp.tool() 
def get_events(stream_id: str) -> list:
    """Get events since last check."""
    return [
        {"type": "rule_broken", "rule": "WALL IS STOP", "timestamp": 1234},
        {"type": "level_won", "timestamp": 1235},
        {"type": "entity_destroyed", "entity": "baba", "cause": "sink"}
    ]
```

### 3. Advanced Navigation

```python
@mcp.tool()
def navigate_menu(path: list[str]) -> str:
    """Navigate game menus. Example: ['worlds', 'island', 'level-3']"""
    
@mcp.tool()
def get_menu_state() -> dict:
    """Get current menu structure and available options."""
    return {
        "current_menu": "world_select",
        "options": [
            {"id": "island", "unlocked": True, "levels": 10},
            {"id": "forest", "unlocked": True, "levels": 8}
        ]
    }
```

### 4. Batch Operations

```python
@mcp.tool()
def execute_plan(moves: list[dict]) -> dict:
    """Execute a sequence of moves with conditions."""
    # Example input:
    [
        {"action": "move", "direction": "up", "times": 3},
        {"action": "push", "target": "text_wall", "direction": "right"},
        {"action": "wait_for", "condition": "rule_broken", "rule": "WALL IS STOP"},
        {"action": "move", "direction": "right", "times": 5}
    ]
    # Returns execution report with any interruptions
```

### 5. State Analysis Tools

```python
@mcp.tool()
def find_path(from_pos: list[int], to_pos: list[int], 
              consider_rules: bool = True) -> list[str]:
    """Find shortest path between positions."""
    
@mcp.tool()
def analyze_rule_implications(hypothetical_rules: list[dict]) -> dict:
    """What would happen if these rules were active?"""
    
@mcp.tool()
def find_text_formations() -> list[dict]:
    """Find all possible rule formations by pushing text."""
```

### 6. Save/Load System

```python
@mcp.tool()
def save_state(name: str) -> str:
    """Save current game state with name."""
    
@mcp.tool()
def load_state(name: str) -> str:
    """Load a previously saved state."""
    
@mcp.tool()
def list_saves() -> list[dict]:
    """List available save states."""
```

### 7. Performance Optimizations

- **WebSocket Communication**: Replace file polling with real-time websocket
- **State Caching**: Only send diffs instead of full state
- **Command Pipelining**: Queue multiple commands without waiting
- **Parallel Instances**: Support multiple game instances

### 8. Enhanced Error Handling

```python
class GameError(Exception):
    pass

@mcp.tool()
def validate_move(direction: str) -> dict:
    """Check if move is valid before executing."""
    return {
        "valid": False,
        "reason": "blocked_by_wall",
        "blocking_entity": {"type": "wall", "pos": [10, 11]}
    }
```

### 9. Learning Support

```python
@mcp.tool()
def record_solution() -> str:
    """Start recording moves for current level."""
    
@mcp.tool()
def save_solution(name: str, tags: list[str]) -> str:
    """Save recorded solution with metadata."""
    
@mcp.tool()
def replay_solution(solution_id: str, speed: float = 1.0) -> str:
    """Replay a saved solution."""
```

### 10. Debug Tools

```python
@mcp.tool()
def get_entity_details(x: int, y: int) -> dict:
    """Get detailed info about entities at position."""
    
@mcp.tool()
def visualize_rules() -> str:
    """Generate visual graph of active rules."""
    
@mcp.tool()
def get_frame_info() -> dict:
    """Get detailed frame timing and performance info."""
```

## Implementation Priority

### Phase 1 (High Impact, Low Effort)
1. Semantic state representation
2. Batch command execution  
3. Better error messages
4. Rule analysis tools

### Phase 2 (High Impact, Medium Effort)
1. Event system
2. Save/load states
3. Path finding
4. Menu navigation

### Phase 3 (Medium Impact, High Effort)
1. WebSocket communication
2. Multiple instances
3. Recording/replay system
4. Visual debugging tools

## Technical Considerations

### Lua Integration
- Extend `io.lua` to capture more game events
- Add hooks for menu navigation
- Implement state serialization

### Data Formats
- Use JSON for all structured data
- Consistent coordinate system [x, y]
- Timestamps for all events

### Backwards Compatibility
- Keep existing tools working
- Add new tools alongside old ones
- Gradual migration path

## Benefits for Agents

1. **Faster Learning**: Semantic state reduces parsing overhead
2. **Better Planning**: Can simulate rule changes before executing
3. **Robustness**: Event system prevents getting stuck
4. **Efficiency**: Batch operations reduce round trips
5. **Debugging**: Save/load helps diagnose failures
6. **Generalization**: Works across all Baba Is You levels

## Example Agent Flow with Improvements

```python
# Old way (current)
state = get_game_state()
# Agent parses ASCII grid, figures out rules manually
execute_commands("up")
state = get_game_state()
# Check if anything changed...

# New way (proposed)
state = get_semantic_state()
# Agent immediately knows: control baba at [16,12], flag at [12,9]
plan = analyze_rule_implications([
    {"subject": "WALL", "verb": "IS", "property": "YOU"}
])
# Agent learns: this would make walls controllable
moves = find_path([16, 12], [10, 13])  # Path to "WALL" text
execute_plan([
    {"action": "move", "path": moves},
    {"action": "push", "target": "text_stop", "direction": "down"},
    {"action": "move", "direction": "up", "until": "reach_flag"}
])
```

This would make the MCP server much more powerful for building intelligent agents!