# Baba Is AGI

A Python implementation of Baba Is You designed for AI agent development. Build autonomous agents to solve puzzles through rule manipulation and strategic planning.

## Features

- Complete game engine with dynamic rule system
- 120+ objects from the original game
- Level loader for official Baba Is You levels
- Multiple agent implementations (random, local search, Claude API)
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

### Run AI Agents

```bash
# Run example random agent
pixi run example-agent

# Run local autonomous agent
pixi run python agent/baba_agent.py --agent-type local

# Run Claude API agent (requires API key)
pixi run python agent/baba_agent.py --agent-type claude
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
env = make("simple")  # or any environment name
grid = env.reset()

# Take action
grid, won, lost = env.step("right")  # or "up", "down", "left"
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
├── baba/                # Core game engine
│   ├── grid.py         # Game grid and mechanics
│   ├── rule.py         # Rule parsing system
│   ├── world_object.py # Game objects
│   └── envs.py         # Pre-built environments
├── agent/              # AI agent implementations
├── scripts/            # Utility scripts
├── tests/              # Comprehensive test suite (102 tests)
└── docs/               # Documentation
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

The codebase is extensively documented with detailed inline comments explaining:
- Game mechanics and rule system
- Object interactions and transformations  
- Level design and environment structure
- Agent development patterns

Additional documentation:
- [Level Format](docs/level_format_analysis.md) - Official .l file structure
- [Level Loader](docs/level_loader_documentation.md) - Loading Baba Is You levels
- [Object Reference](docs/object_reference.md) - Complete object listing

## License

Based on [baba-is-ai](https://github.com/nacloos/baba-is-ai).