# Baba Is AGI

Python implementation of Baba Is You for building AI agents.

## Features

- Complete game engine with dynamic rule system
- 120+ objects from the original game
- Level loader for official Baba Is You levels
- Claude Code agent that plays autonomously
- 14 built-in environments of varying difficulty

## Installation

```bash
# Install pixi
curl -fsSL https://pixi.sh/install.sh | bash

# Install dependencies
pixi install
```

### Optional: Official Sprites

If you own Baba Is You on Steam:
```bash
pixi run python scripts/setup_sprites.py
```

## Quick Start

### Play Interactively

```bash
pixi run play
```

Controls: Arrow keys/WASD to move, R to reset, Q to quit

### Run the AI Agent

```bash
# Watch Claude Code solve puzzles
pixi run python agent/claude_code_agent.py

# Step through moves interactively  
pixi run python agent/claude_code_agent.py --interactive
```

### Load Official Levels

```python
from baba.level_loader import LevelLoader
from baba.registration import Registry

loader = LevelLoader()
registry = Registry()
grid = loader.load_level("baba", 0, registry)
```

## Creating Agents

```python
from baba import make

# Create environment
env = make("SimpleEnvironment-v0")
obs = env.reset()

# Take action (0=up, 1=right, 2=down, 3=left)
obs, reward, done, info = env.step(1)
```

## Game Rules

Rules are formed by arranging text blocks:
- `BABA IS YOU` - Control Baba
- `FLAG IS WIN` - Touch flag to win
- `WALL IS STOP` - Walls block movement
- `ROCK IS PUSH` - Rocks can be pushed
- `BABA IS WALL` - Transform Baba into walls

## Project Structure

```
baba-is-agi/
├── baba_is_you/         # Core game engine
├── agent/               # AI agents
├── scripts/             # Utility scripts
├── docs/               # Documentation
└── tests/              # Test suite
```

## Available Environments

Basic:
- `simple` - Introduction level
- `wall_maze` - Navigate walls
- `push_puzzle` - Push objects

Advanced:
- `make_win` - Create WIN rule
- `two_room_break_stop` - Break rules to pass
- `transform_puzzle` - Use transformations
- `rule_chain` - Complex rule sequences

List all with: `pixi run python scripts/list_environments.py`

## Documentation

- [Level Format](docs/level_format_analysis.md) - File structure details
- [Level Loader](docs/level_loader_documentation.md) - Loading official levels
- [Object Reference](docs/object_reference.md) - All objects and properties

## License

Based on [baba-is-ai](https://github.com/nacloos/baba-is-ai).