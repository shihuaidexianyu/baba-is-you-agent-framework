# Baba Is AGI Agent Framework

This directory contains a programmable visual agent framework for playing Baba Is You.

## Architecture Overview

The framework is designed around a clean separation of concerns:

```
BabaAgent (Visual GUI Manager)
    ├── Environment Management
    ├── Pygame Rendering
    └── Delegates to → DecisionMaker (Abstract Interface)
                            ├── SimplePathfindingDecisionMaker
                            ├── InteractiveDecisionMaker
                            └── [Your Custom DecisionMaker]
```

## Core Concepts

### GameObservation
A structured representation of the game state that includes:
- Controlled objects (YOU property)
- Win objects (WIN property)  
- Pushable objects (PUSH property or text)
- Stop objects (STOP property)
- Active rules
- Visual grid array

### AgentDecision
The output of a DecisionMaker containing:
- `action`: The chosen Action (UP, DOWN, LEFT, RIGHT)
- `reasoning`: Explanation of the decision
- `confidence`: How confident the agent is (0.0 to 1.0)
- `metadata`: Optional additional data

### DecisionMaker Interface
The core extensibility point. Implement this abstract class to create new agent behaviors:

```python
class DecisionMaker(ABC):
    @abstractmethod
    def decide(self, observation: GameObservation) -> AgentDecision:
        """Make a decision based on game state."""
        pass
    
    def reset(self):
        """Called at episode start."""
        pass
```

## Creating Custom Decision Makers

To extend the agent with new capabilities (e.g., tool use, LLM integration):

```python
from agent.baba_agent import DecisionMaker, GameObservation, AgentDecision, Action

class MyCustomDecisionMaker(DecisionMaker):
    def decide(self, observation: GameObservation) -> AgentDecision:
        # Your decision logic here
        # Access game state via observation
        # Return AgentDecision with action and reasoning
        
        return AgentDecision(
            action=Action.RIGHT,
            reasoning="My custom logic says go right",
            confidence=0.8
        )

# Use it
from agent.baba_agent import BabaAgent
agent = BabaAgent(decision_maker=MyCustomDecisionMaker())
agent.play_episode()
```

## Usage

### Command Line
```bash
# Play any level with the agent
pixi run play simple
pixi run play two_room
pixi run play make_win

# List available levels
pixi run list-envs

# Direct agent usage (for development)
pixi run python -m agent.baba_agent --env make_win --episodes 5 --delay 0.3
```

### Python API
```python
from agent.baba_agent import BabaAgent, SimplePathfindingDecisionMaker

# Create agent with custom decision maker
agent = BabaAgent(
    env_name="two_room",
    decision_maker=SimplePathfindingDecisionMaker(),
    delay=0.5,
    show_info_panel=True
)

# Play single episode
won = agent.play_episode(max_steps=100)

# Play multiple episodes and get stats
stats = agent.play_episodes(num_episodes=5, max_steps=100)
print(f"Win rate: {stats['win_rate']:.1%}")

# Clean up
agent.cleanup()
```

## Built-in Decision Makers

### SimplePathfindingDecisionMaker
- Uses BFS pathfinding to reach goals
- Explores for text objects when can't win directly
- Good baseline for simple puzzles

## Visual Features

- **Real-time rendering**: See the game state update
- **Info panel**: Shows current decision maker, action, reasoning, and confidence
- **Pause control**: Press SPACE to pause
- **Victory/defeat animations**: Clear feedback on episode end

## Extending for Tool Use

The framework is designed to support tool-using agents. Here's the pattern:

```python
class ToolUsingDecisionMaker(DecisionMaker):
    def __init__(self):
        self.tools = {
            'pathfinder': PathfinderTool(),
            'rule_analyzer': RuleAnalyzerTool(),
            'strategy_selector': StrategyTool()
        }
    
    def decide(self, observation: GameObservation) -> AgentDecision:
        # Use tools to analyze the situation
        path = self.tools['pathfinder'].find_best_path(observation)
        rule_opportunities = self.tools['rule_analyzer'].analyze(observation)
        
        # Combine tool outputs to make decision
        strategy = self.tools['strategy_selector'].select(
            path, rule_opportunities, observation
        )
        
        return strategy.to_decision()
```

## Performance Considerations

- Visual rendering adds overhead (~60 FPS cap)
- Delay between actions is configurable
- GameObservation is lightweight - just references and lists
- DecisionMakers can maintain state between calls

## Future Extensions

The architecture supports:
- LLM-based decision makers (Claude API integration)
- Multi-step planning with rollouts
- Learning from demonstrations
- Tool orchestration frameworks
- Parallel environment execution