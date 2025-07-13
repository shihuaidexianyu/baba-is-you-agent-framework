# Baba Is AGI

An autonomous agent that plays Baba Is You using the Claude Code SDK and MCP (Model Control Protocol).

## Quick Start

1. **Install dependencies**:
   ```bash
   pixi install
   ```

2. **Setup the game** (one-time setup):
   ```bash
   pixi run setup
   ```
   This will:
   - Find your Baba Is You installation
   - Install the necessary mod files
   - Update `config.toml` with your game path

3. **Play a level**:
   ```bash
   pixi run play 1  # Play level 1
   pixi run play 5  # Play level 5
   pixi run play    # Play default level (from config.toml)
   ```

## Configuration

Edit `config.toml` to customize:
- Game installation path
- MCP server settings
- Agent behavior (max turns, default level, etc.)

## Advanced Usage

### Run without starting the game
```bash
pixi run play 1 --no-game
```

### Run only the MCP server
```bash
pixi run play --mcp-only
```

### Test MCP connection
```bash
pixi run test-mcp
```

## How It Works

1. **Game Integration**: A Lua mod (`io.lua`) hooks into Baba Is You to read/write game state
2. **MCP Server**: Python server provides tools for game control (move, undo, restart, etc.)
3. **Claude Agent**: Uses Claude Code SDK to analyze the game and make strategic moves
4. **Orchestration**: The `play` command starts everything in the right order

## Requirements

- Baba Is You (Steam version tested)
- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable

## Troubleshooting

- **"No state available"**: Make sure the game is running and a level is loaded
- **Commands not executing**: Check that `io.lua` is in the game's Data folder
- **MCP connection fails**: Run `pixi run test-mcp` to debug

## Development

See `CLAUDE.md` for detailed development documentation.