baba-is-agi/
├── baba/                 # Core game implementation
│   ├── grid.py           # Game grid and main logic
│   ├── world_object.py   # Game objects and text blocks
│   ├── rule.py           # Rule parsing and management
│   ├── properties.py     # Game properties (YOU, WIN, STOP, etc.)
│   ├── rendering.py      # Basic rendering utilities
│   ├── sprites.py        # Custom ASCII sprite generation
│   ├── sprite_loader.py  # Loads official sprites if available
│   ├── level_loader.py   # Loads official Baba Is You levels
│   ├── envs.py           # All game environments (14 total)
│   ├── agent.py          # Base Agent class
│   └── assets/sprites/   # Directory for official game sprites (gitignored)
├── agents/               # Agent implementations
│   ├── random_agent.py   # Simple random agent
│   ├── demo_agent.py     # Greedy pathfinding agent
│   └── claude_code_agent.py # Claude API agent
├── scripts/              # Utility scripts
├── tests/                # Comprehensive test suite (102 tests)
├── docs/                 # Documentation
└── pixi.toml            # Dependency management

# Baba Is You Agent Framework (Minimal Edition)

This trimmed-down repository keeps only the essentials required to experiment
with the Baba Is You game engine and two baseline agents (random and demo).
Everything else—documents, auxiliary scripts, additional agents, and tests—has
been removed for clarity per the latest cleanup request.

## Included Components

- `baba/`: complete game engine, rule system, and built-in puzzle environments.
- `agents/random_agent.py`: very small baseline that samples actions uniformly.
- `agents/demo_agent.py`: deterministic breadth-first-style solver that knows
    how to push objects.
- `pyproject.toml` / `pixi.toml`: dependency definitions to install and run the
    engine and agents.

## Installation

```bash
pip install -e .
```

The editable install pulls in core runtime dependencies (NumPy, Pygame, etc.)
defined in `pyproject.toml`.

## Running the Game Engine

```bash
python -m baba.play
```

Controls: arrow keys or WASD to move, `R` to reset a level, `Q` to quit.

## Baseline Agents

Random agent:

```bash
python agents/random_agent.py
```

Demo agent with pathfinding:

```bash
python agents/demo_agent.py
```

Both entry points create the default `simple` environment and render the game
window using Pygame. Modify the scripts if you want to target a different
environment.

## Folder Layout

```
baba-is-you-agent-framework/
├── baba/            # Core engine and environments
├── agents/
│   ├── demo_agent.py
│   └── random_agent.py
├── pixi.toml
├── pyproject.toml
└── README.md
```

## Notes

- Official Baba Is You assets and levels are still supported by the engine, but
    you must own the game to use them.
- To build custom agents, implement `baba.agent.Agent` and call
    `play_episode()` just like the demo script does.
