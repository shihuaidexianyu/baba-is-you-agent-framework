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

- **max_turns=None**: Unlimited turns for extended thinking and reasoning
- **continue_conversation=True**: Persists conversation throughout entire episode (after step 1)
- **permission_mode**: Bypasses permission prompts for uninterrupted gameplay

### Session Persistence

The agent maintains a single Claude conversation throughout the entire game episode:
- First step: Starts new conversation with full context
- Subsequent steps: Uses `continue_conversation=True` to maintain context
- Claude retains memory of all previous states and actions
- Enables more sophisticated reasoning and strategy development

## State Representation

The agent receives a detailed textual description of the game state through the `_describe_state()` method:

### 1. Game Rules Reminder

```
GAME RULES: To win, YOU must touch an object that IS WIN.
You can push objects and text. Pushing text can change rules.
IMPORTANT: The X boundary is solid - you cannot move through it or push objects through it!
Objects pushed against the boundary will not move. Plan your pushes carefully.
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

**Grid Format Example:**
```
Grid Layout:
- Map boundary: X (solid wall - cannot move or push through)
- Empty cells: .
- Objects (game pieces): lowercase (e.g., baba, rock, flag)
- Text (rule pieces): UPPERCASE (e.g., BABA, IS, YOU)
- Multiple objects in same cell: joined with + (e.g., rock+flag)

     0    1    2    3    4    5    6    7    8    9  
   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 0|X .   BABA  IS  YOU   .   ROCK  IS  PUSH  .    .X
 1|X .    .    .    .    .    .    .    .    .    .X
 2|X .    .   wall wall wall wall wall wall wall  .X
 3|X .    .   wall  .    .    .    .    .   wall  .X
 4|X .   baba  .   rock  .   rock  .   rock  .   flagX
 5|X .    .   wall  .    .    .    .    .   wall  .X
 6|X .    .   wall wall wall wall wall wall wall  .X
 7|X .   FLAG  IS  WIN   .   WALL  IS  STOP  .    .X
   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Objects in grid:
  Game objects: baba, flag, rock, wall
  Text objects: BABA, FLAG, IS, STOP, WALL, WIN, YOU
```

- **Full object names**: No truncation, making rules clear
- **Coordinate system**: Row and column numbers for reference
- **Clear spacing**: Each cell properly aligned
- **Object legend**: Lists all unique objects and text in the grid

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
   - Shows overlapping objects with + notation

3. **History Tracking**
   - Provides complete game history with both states and actions
   - For each step, shows:
     - The full game state before the action
     - The action taken and its reasoning
   - Session persists across entire episode
   - Helps Claude understand how the game evolved and avoid repeating failed strategies

4. **Prompt Construction**
   - First step includes full instructions
   - Subsequent steps include action history
   - Always requests JSON response format

5. **Claude Query**
   - Sends prompt with state description and history
   - 30-second timeout per move
   - Uses `continue_conversation` after first query
   - Unlimited turns for extended thinking

6. **Response Processing**
   - Attempts to parse JSON response
   - Falls back to keyword extraction if JSON fails
   - Last resort: heuristic movement toward goal

## Example Interaction

### First Step Prompt

```
Baba Is You puzzle. Remember: YOU must touch WIN to win. You can push objects.

Current state:
GAME RULES: To win, YOU must touch an object that IS WIN.
You can push objects and text. Pushing text can change rules.
IMPORTANT: The X boundary is solid - you cannot move through it or push objects through it!
Objects pushed against the boundary will not move. Plan your pushes carefully.

Active Rules:
  BABA IS YOU
  ROCK IS PUSH
  FLAG IS WIN
  WALL IS STOP

YOU control: BABA
WIN objects: FLAG
PUSH objects: ROCK
STOP objects: WALL

Grid Layout:
- Empty cells: .
- Objects (game pieces): lowercase (e.g., baba, rock, flag)
- Text (rule pieces): UPPERCASE (e.g., BABA, IS, YOU)

       0         1         2         3         4         5         6         7         8         9     
   ----------------------------------------------------------------------------------------------------
0|     .        BABA       IS       YOU        .        ROCK       IS       PUSH       .         .
1|     .         .         .         .         .         .         .         .         .         .
2|     .         .        wall      wall      wall      wall      wall      wall      wall       .
3|     .         .        wall       .         .         .         .         .        wall       .
4|     .        baba       .        rock       .        rock       .        rock       .        flag
5|     .         .        wall       .         .         .         .         .        wall       .
6|     .         .        wall      wall      wall      wall      wall      wall      wall       .
7|     .        FLAG       IS       WIN        .        WALL       IS       STOP       .         .

Objects in grid:
  Game objects: baba, flag, rock, wall
  Text objects: BABA, FLAG, IS, PUSH, ROCK, STOP, WALL, WIN, YOU

Key positions:
  baba (YOU) at (1,4)
  flag (WIN) at (9,4)

What's your move? Respond with only JSON:
{"action": "right", "reasoning": "move toward flag"}

Your JSON response:
```

### Subsequent Step Prompts (with Full History)

```
Step 3:

Complete game history:

================================================================================
Step 1:
State before action:
GAME RULES: To win, YOU must touch an object that IS WIN.
[Full grid showing baba at (1,4), rocks at (3,4), (5,4), (7,4), flag at (9,4)]

Action taken: right - Move baba right toward flag at (9,4)

================================================================================
Step 2:
State before action:
GAME RULES: To win, YOU must touch an object that IS WIN.
[Full grid showing baba at (2,4), rocks unchanged]

Action taken: right - Push rock at (3,4) right to clear path

================================================================================
Current state:
GAME RULES: To win, YOU must touch an object that IS WIN.
[Full grid showing baba at (3,4), rock pushed to (4,4), other rocks at (5,4), (7,4), flag+rock at (9,4)]

Next move as JSON:
```

The complete history helps Claude:
- See exactly how each action changed the game state
- Understand which objects moved and why
- Track progress toward the goal
- Recognize patterns and adjust strategy

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

With the improved grid representation, Claude now provides more specific reasoning:

```json
Step 1: {"action": "right", "reasoning": "Move baba right toward flag at (8,5)"}
Step 2: {"action": "right", "reasoning": "push rock at (3,4) right to clear path"}
Step 3: {"action": "right", "reasoning": "push rock at (8,4) to move it and reach flag underneath at (9,4)"}
Step 14: {"action": "down", "reasoning": "move down to potentially manipulate the FLAG IS WIN rule text"}
```

Claude can now:
- Reference exact coordinates
- Identify when objects might be overlapping
- Consider rule manipulation as an alternative strategy

## Key Design Decisions

1. **Text-Based Representation**: Makes game state interpretable by language models
2. **Full Object Names**: No truncation - shows complete names like `baba`, `rock`, `flag`
3. **Coordinate System**: Row/column numbers make positions unambiguous
4. **Clear Object/Text Distinction**: Lowercase for objects, UPPERCASE for text
5. **Explicit Rule Communication**: Clearly states win conditions and mechanics
6. **JSON Response Format**: Structured output for reliable parsing
7. **Reasoning Requirement**: Provides insight into agent's decision process
8. **Conversation Continuity**: Uses `continue_conversation` for efficiency
9. **Timeout Protection**: 30-second limit prevents infinite waiting
10. **Graceful Fallbacks**: Multiple strategies if response parsing fails

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