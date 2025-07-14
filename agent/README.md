# Baba Is AGI Agents

AI agents for playing Baba Is You puzzles.

## Agent Types

- **LocalAgent**: Autonomous agent with pathfinding and rule analysis
- **APIAgent**: Claude API-based agent (requires API key)
- **VisualAgent**: Adds pygame visualization to any agent

## Quick Start

```bash
# Run autonomous agent
pixi run agent-local

# With visualization
pixi run agent-visual

# Using Claude API
export ANTHROPIC_API_KEY=your_key
pixi run agent-api
```

## Python Usage

```python
from agent.baba_agent import create_agent

# Create and run agent
agent = create_agent("local", environment="make_win")
won = agent.play_episode(max_steps=50)

# With visualization
agent = create_agent("visual", base_agent="local", environment="make_win")
```

## Creating Custom Agents

See [CLAUDE.md](CLAUDE.md) for the agent framework documentation.