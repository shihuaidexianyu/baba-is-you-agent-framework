# Baba Is AGI - Claude Development Guide

This project creates an autonomous agent that plays Baba Is You using the Claude Code SDK and MCP (Model Control Protocol).

## Project Structure

```
baba-is-agi/
├── baba_agent/           # Agent implementation
│   ├── baba_agent_sdk.py # Main agent using Claude Code SDK
│   ├── test_connection.py # MCP connection tester
│   ├── pixi.toml         # Python dependencies
│   └── README.md         # User documentation
├── baba_is_eval/         # MCP server for game interface
│   ├── game_mcp.py       # MCP server (no pyautogui)
│   ├── io.lua            # Lua mod for game communication
│   ├── help_rules.json   # Game rules documentation
│   ├── setup.sh          # Installation script
│   └── README.md         # Setup instructions
└── CLAUDE.md             # This file
```

## Architecture

### Communication Flow
1. **Game ↔ Lua Mod**: The `io.lua` file hooks into Baba Is You to read/write game state
2. **Lua Mod ↔ File System**: Game state written to `world_data.txt`, commands read from `commands/*.lua`
3. **MCP Server ↔ Files**: `game_mcp.py` reads state files and writes command files
4. **Claude ↔ MCP**: Claude Code SDK connects to MCP server and uses tools
5. **Agent ↔ Claude**: `baba_agent_sdk.py` orchestrates Claude to play the game

### Key Design Decisions
- **No pyautogui**: All game control is programmatic through Lua commands
- **State persistence**: Game state saved to INI file for reliable reading
- **Command queue**: Numbered Lua files ensure proper command ordering
- **MCP tools**: Clean interface for game actions (move, undo, restart, etc.)

## Running the Agent

1. **Prerequisites**:
   - Baba Is You installed (Steam version tested)
   - Python 3.11+
   - `ANTHROPIC_API_KEY` environment variable set

2. **Setup**:
   ```bash
   # Install baba_is_eval in game's Data folder
   cd "/path/to/Baba Is You/Data"
   git clone <repo> .
   cd baba_is_eval
   ./setup.sh
   
   # Install agent dependencies
   cd ../baba_agent
   pixi install
   ```

3. **Run**:
   ```bash
   # Start Baba Is You game first
   # Then run the agent
   cd baba_agent
   pixi run python baba_agent_sdk.py
   ```

## MCP Tools Available

- `enter_level(level: str)`: Enter a level (e.g., "1", "2", "3")
- `get_game_state()`: Get current board as ASCII grid
- `execute_commands(commands: str)`: Move with "up,down,left,right"
- `game_rules(topic: str)`: Get help on game mechanics
- `restart_level()`: Restart current level
- `undo_multiple(n: int)`: Undo n moves
- `leave_level()`: Exit level (quits game)

## Key Concepts

### Game State Format
The game state is displayed as an ASCII grid:
```
y/x |  1  |  2  |  3  
----+-----+-----+-----
 1  |     | baba|     
 2  | wall| flag| text_is
```

Objects on same tile show with `<` separator: `wall<text_push`

### Rule System
- Rules form from text: `BABA IS YOU`, `WALL IS STOP`, `FLAG IS WIN`
- Text blocks can be pushed to modify rules
- Breaking rules changes game mechanics instantly

### Agent Strategy
The agent should:
1. Identify active rules by scanning for text patterns
2. Determine what it controls (IS YOU)
3. Find win conditions (IS WIN)
4. Plan rule modifications if needed
5. Execute movement to achieve goals

## Common Development Tasks

### Testing MCP Connection
```bash
pixi run python test_connection.py
```

### Modifying Agent Behavior
Edit the prompt in `baba_agent_sdk.py` to change how Claude approaches the game.

### Adding New MCP Tools
1. Add tool method in `game_mcp.py` with `@mcp.tool()` decorator
2. Implement game interaction via Lua commands
3. Update agent prompt to mention new tool

### Debugging Game State
- Check `/Data/Worlds/baba/world_data.txt` for raw state
- Look in `/Data/baba_is_eval/commands/` for command files
- Game must be running and level loaded for state updates

## Troubleshooting

### "No state available"
- Ensure game is running and level is loaded
- Run `setup.sh` again
- Check file permissions on game directories

### Commands not executing
- Verify command files being created in `commands/` directory
- Check `io.lua` is properly loaded (restart game after setup.sh)
- Ensure no syntax errors in Lua command files

### MCP connection fails
- Check game path in `game_mcp.py` matches your installation
- Verify all Python dependencies installed
- Test with `test_connection.py` first

## Performance Considerations

- **State polling**: Currently polls file system, could use file watchers
- **Command latency**: ~0.5s delay for command execution
- **Claude turns**: Limited to 50 turns per session to control costs

## Future Improvements

1. **Better level navigation**: Currently hardcoded for levels 1-7
2. **State diffing**: Show what changed between moves
3. **Planning mode**: Let Claude plan multiple moves ahead
4. **Parallel execution**: Run multiple game instances
5. **Learning**: Store successful solutions for replay
6. **Vision**: Use screenshots for more complex scenarios
7. **WebSocket MCP**: Replace file polling with real-time updates

## Code Style

- Use type hints for function parameters
- Document MCP tools thoroughly 
- Keep agent prompts clear and structured
- Test changes with `test_connection.py` first

## Environment Variables

- `ANTHROPIC_API_KEY`: Required for Claude API access
- Game path can be configured in `config.yaml` (optional)

## Security Notes

- MCP server only exposes game control, no file system access
- Command validation prevents arbitrary Lua execution
- State files use restricted paths only