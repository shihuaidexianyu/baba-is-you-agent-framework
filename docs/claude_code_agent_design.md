# Claude Code Agent Design Documentation

This document describes the design and implementation of the Claude Code Agent for Baba Is You, including the prompts, state representation, and information flow.

## Overview

The Claude Code Agent uses the Claude Code SDK to analyze game states and make decisions. It receives a textual representation of the game state and returns JSON-formatted actions with reasoning.

## System Architecture

### Agent Initialization

```python
class ClaudeCodeAgent(Agent):
    def __init__(self, verbose=True):
        super().__init__("Claude Code Agent")
        self.verbose = verbose
        self.conversation_history = []  # Track conversation for context
        self.episode_steps = 0
        self.session_active = False
        self.last_reasoning = ""  # Store reasoning for UI display
```

The agent maintains:
- **Conversation history**: Currently tracked but not actively used
- **Episode steps**: Counter for the current episode
- **Session state**: Whether a Claude conversation is active (for `continue_conversation` optimization)
- **Last reasoning**: Displayed in the game UI

## Claude Configuration

### System Prompt

```python
system_prompt = 'You are playing Baba Is You. To win: move YOUR object to touch a WIN object. You can push objects and text. Pushing text changes rules. ALWAYS respond with only valid JSON: {"action": "<direction>", "reasoning": "<brief explanation>"}. Direction must be one of: up, down, left, right.'
```

Key points communicated:
1. Win condition: YOU touches WIN
2. Core mechanics: Can push objects and text
3. Rule manipulation: Pushing text changes rules
4. Required response format: JSON with action and reasoning
5. Valid actions: up, down, left, right

### Claude Options

```python
options = ClaudeCodeOptions(
    max_turns=1,
    system_prompt=system_prompt,
    continue_conversation=self.session_active,
    permission_mode="bypassPermissions",  # No prompts during game
)
```

- **max_turns=1**: Single response per query
- **continue_conversation**: Reuses conversation after first turn for efficiency
- **permission_mode**: Bypasses permission prompts for uninterrupted gameplay

## State Representation

The agent receives a detailed textual description of the game state through the `_describe_state()` method:

### 1. Game Rules Reminder

```
GAME RULES: To win, YOU must touch an object that IS WIN.
You can push objects and text. Pushing text can change rules.
```

### 2. Active Rules

```
Active Rules:
  BABA IS YOU
  ROCK IS PUSH
  FLAG IS WIN
  WALL IS STOP
```

### 3. Object Properties

```
YOU control: baba
WIN objects: flag
PUSH objects: rock
STOP objects: wall
```

### 4. Grid Representation

```
Grid (lowercase=objects, UPPERCASE=text):
bab  .  .  .  .  .  .  .  .  fla
.    .  .  .  .  .  .  .  .  .
walwalwalwalwalwalwalwalwal.  .
```

- **Lowercase**: Game objects (baba, rock, flag, wall)
- **UPPERCASE**: Text objects (BABA, IS, YOU, etc.)
- **Dots (.)**: Empty spaces
- Objects are truncated to 3 characters for alignment

### 5. Key Positions

```
Key positions:
  baba (YOU) at (0,0)
  flag (WIN) at (9,0)
```

Lists positions of YOU-controlled objects and WIN objects with coordinates.

## Information Flow

### Step-by-Step Process

1. **Game State Analysis**
   - Rule manager extracts active rules
   - Identifies YOU, WIN, PUSH, and STOP objects
   - Maps object positions on grid

2. **State Description Generation**
   - Converts grid to text representation
   - Formats rules and object properties
   - Lists key object positions

3. **Prompt Construction**
   - First step includes full instructions
   - Subsequent steps are more concise
   - Always requests JSON response format

4. **Claude Query**
   - Sends prompt with state description
   - 30-second timeout per move
   - Uses `continue_conversation` after first query

5. **Response Processing**
   - Attempts to parse JSON response
   - Falls back to keyword extraction if JSON fails
   - Last resort: heuristic movement toward goal

## Example Interaction

### First Step Prompt

```
Baba Is You puzzle. Remember: YOU must touch WIN to win. You can push objects.

GAME RULES: To win, YOU must touch an object that IS WIN.
You can push objects and text. Pushing text can change rules.

Active Rules:
  BABA IS YOU
  ROCK IS PUSH
  FLAG IS WIN
  WALL IS STOP

YOU control: baba
WIN objects: flag
PUSH objects: rock
STOP objects: wall

Grid (lowercase=objects, UPPERCASE=text):
bab  .  roc  .  roc  .  roc  .  .  fla
[... rest of grid ...]

Key positions:
  baba (YOU) at (1,4)
  flag (WIN) at (9,4)

What's your move? Respond with only JSON:
{"action": "right", "reasoning": "move toward flag"}

Your JSON response:
```

### Subsequent Step Prompts

```
Step 2:
[State description]

Next move as JSON:
```

## Response Handling

### Expected Response Format

```json
{
  "action": "right",
  "reasoning": "push rock right to clear path"
}
```

### Fallback Mechanisms

1. **JSON Parsing**: Try to extract JSON from response
2. **Keyword Search**: Look for direction words in response
3. **Heuristic Movement**: Move toward nearest WIN object

### Example Claude Responses

```
Step 1: {"action": "right", "reasoning": "move toward flag"}
Step 2: {"action": "right", "reasoning": "push first rock right"}
Step 3: {"action": "up", "reasoning": "try alternate path around rocks"}
```

## Key Design Decisions

1. **Text-Based Representation**: Makes game state interpretable by language models
2. **Explicit Rule Communication**: Clearly states win conditions and mechanics
3. **JSON Response Format**: Structured output for reliable parsing
4. **Reasoning Requirement**: Provides insight into agent's decision process
5. **Conversation Continuity**: Uses `continue_conversation` for efficiency
6. **Timeout Protection**: 30-second limit prevents infinite waiting
7. **Graceful Fallbacks**: Multiple strategies if response parsing fails

## Limitations and Considerations

1. **No Visual Input**: Agent doesn't see actual sprites, only text representation
2. **Limited Context**: Each move is relatively independent (though conversation continues)
3. **Rule Complexity**: Complex rule chains might be hard to represent textually
4. **Grid Size**: Large grids might exceed context limits
5. **Response Variability**: Claude might not always return valid JSON despite instructions

## Future Improvements

1. **Memory System**: Better use of conversation history
2. **Planning**: Multi-step lookahead capability
3. **Rule Reasoning**: Explicit rule manipulation strategies
4. **State Abstraction**: Higher-level game state descriptions
5. **Learning**: Incorporate successful strategies from past games