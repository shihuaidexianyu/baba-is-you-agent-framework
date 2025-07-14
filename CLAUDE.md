# Claude Code Context for Baba Is AGI

This document provides essential context for Claude Code when working on this repository.

## Documentation

- [Level Format](docs/level_format_analysis.md) - Baba Is You file format details
- [Level Loader](docs/level_loader_documentation.md) - How to load official levels
- [Object Reference](docs/object_reference.md) - Complete list of all 120+ objects
- [Agent Framework](agent/CLAUDE.md) - How to create custom AI agents
- [Test Suite](tests/README.md) - Running and writing tests

## Core Philosophy: LEAN AND CLEAN

This is a **research project**. Keep the codebase minimal and focused:

- **NO backwards compatibility layers** - We move fast and break things
- **NO deprecation warnings** - Just change the API when needed
- **NO unnecessary abstractions** - Write simple, direct code
- **NO defensive programming** - Assume competent users
- **NO compatibility shims** - One way to do things
- **REMOVE code liberally** - If it's not actively used, delete it

When in doubt, choose simplicity over compatibility. This is research code that should be easy to understand, modify, and experiment with.

## Project Overview

Python implementation of Baba Is You designed for building AI agents. The project includes:
- Complete game engine with rule manipulation mechanics
- 14 pre-built environments of varying difficulty
- Agent framework for building autonomous players
- Visual rendering with Pygame
- Managed with Pixi for consistent environments across platforms

## Key Technical Details

### Pixi Dependency Management

This project uses **Pixi** for environment and dependency management. Pixi ensures consistent Python environments across all platforms without the need for manual virtualenv setup or path manipulation.

**Important Pixi Guidelines:**
- NEVER use `sys.path` manipulation in Python files - Pixi handles all path setup
- NEVER manually install packages with pip - add them to `pixi.toml` instead
- All scripts should have corresponding pixi tasks defined in `pixi.toml`
- Always run commands through pixi: `pixi run <task-name>`

**Initial Setup:**
```bash
pixi install               # Install dependencies
pixi run install-dev       # Install package in editable mode
```

**Available Pixi Tasks:**
```bash
# Core functionality
pixi run play              # Play the game interactively
pixi run test              # Run test suite

# Agent tasks
pixi run agent             # Run the default agent
pixi run agent-visual      # Run agent with GUI visualization
pixi run agent-local       # Run local autonomous agent
pixi run agent-api         # Run Claude API agent (requires key)
pixi run watch-agent       # Watch agent play (legacy)

# Environment and sprites
pixi run list-envs         # List all available environments
pixi run setup-sprites     # Copy official sprites from Steam
pixi run demo-sprites      # Demo sprite rendering
pixi run sprite-showcase   # Show all available sprites

# Development
pixi run example-agent     # Run example random agent
pixi run custom-level      # Demo custom level creation

# Code Quality
pixi run lint              # Check code with Ruff linter
pixi run lint-fix          # Auto-fix linting issues
pixi run format            # Format code with Ruff
pixi run format-check      # Check formatting without changes
pixi run typecheck         # Run Ty type checker
pixi run pre-commit-install # Install git pre-commit hooks
pixi run pre-commit-run    # Manually run all pre-commit hooks
```

**Adding New Dependencies:**
Edit `pixi.toml` and add to the `[dependencies]` section:
```toml
[dependencies]
new-package = ">=1.0"
```

Then run `pixi install` to update the environment.

### Project Structure
```
baba-is-agi/
├── baba/                 # Core game implementation
│   ├── grid.py           # Game grid and main logic
│   ├── world_object.py   # Game objects and text blocks
│   ├── rule.py           # Rule parsing and management
│   ├── properties.py     # Game properties (YOU, WIN, STOP, etc.)
│   ├── rendering.py      # Basic rendering utilities
│   ├── sprites.py        # Custom sprite generation
│   ├── sprite_loader.py  # Loads official sprites if available
│   ├── envs.py           # All game environments (14 total)
│   └── assets/sprites/   # Directory for official game sprites (gitignored)
├── agent/                # Agent implementations
│   ├── baba_agent.py     # All agent types in single module
│   └── README.md         # Agent documentation
├── scripts/              # Utility scripts
└── pixi.toml            # Dependency management
```

### Sprite System

The game uses a dual sprite system:
1. **Custom sprites** (always available): ASCII-art based sprites defined in `sprites.py`
2. **Official sprites** (optional): Real game sprites from Steam installation

**Important**: Official sprites are copyrighted and should NEVER be committed to git. They are:
- Stored in `baba/assets/sprites/` (entire directory is gitignored)
- Automatically detected and used if present
- Fall back to custom sprites if not found

To set up official sprites (only for users who own the game):
```bash
pixi run setup-sprites
```

### Environment Interface

The game environments follow a custom interface (not OpenAI Gym):
- `env.reset()` returns a Grid object
- `env.step(action)` takes string actions ("up", "down", "left", "right")
- `env.step()` returns tuple: (grid, won, lost)
- The Grid object has methods like `render()` and properties like `rule_manager`

### Agent Development

When developing agents:
- Use `Property` enum from `properties.py` for rule checking
- Access grid cells with `grid.grid[y][x]` (returns set of Objects)
- Check properties with `grid.rule_manager.has_property(obj_name, Property.YOU)`
- Text objects have `is_text = True`

### Common Pitfalls

1. **Circular imports**: Be careful with imports between rule.py, world_object.py, and properties.py
2. **Object hashing**: Objects must be hashable to be stored in grid sets
3. **String formatting**: Avoid nested f-strings in list comprehensions
4. **Grid coordinates**: Grid uses [y][x] indexing, not [x][y]

### Testing

To test the game:
```bash
pixi run play           # Play interactively
pixi run agent-local    # Watch autonomous AI play
pixi run agent-visual   # Watch AI with GUI visualization
pixi run list-envs      # See all available environments
pixi run test           # Run test suite
```

### Code Quality

This project uses automated code quality tools:

**Linting & Formatting:**
- **Ruff** for Python linting and formatting (configuration in `pyproject.toml`)
- Line length: 100 characters
- Double quotes for strings
- Automatic import sorting

**Type Checking:**
- **Ty** for type checking (Astral's new Rust-based type checker)
- Note: Ty is in preview/beta, expect some rough edges

**Pre-commit Hooks:**
- Automatically run on every commit
- Checks linting, formatting, and types
- Install with: `pixi run pre-commit-install`

**Before committing:**
```bash
pixi run lint           # Check for linting issues
pixi run format         # Auto-format code
pixi run typecheck      # Check types
```

Or run all checks at once:
```bash
pixi run pre-commit-run
```