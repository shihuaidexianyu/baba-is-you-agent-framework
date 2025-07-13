# Baba Is You AI Agent

An autonomous agent that plays Baba Is You using Claude Code SDK and the MCP (Model Control Protocol) server.

## Features

- **Autonomous Gameplay**: The agent analyzes game states and makes decisions using Claude AI
- **MCP Integration**: Communicates with Baba Is You through the MCP server interface
- **Game State Analysis**: Understands rules, win conditions, and possible moves
- **Strategic Planning**: Plans moves to achieve level objectives
- **Claude Code SDK**: Uses the official SDK for reliable Claude integration

## Quick Start

If you haven't already set up the project, see the main README.md in the root directory.

To run the agent:
```bash
# From the root directory
pixi run play 1  # Play level 1
```

## Architecture

### Main Components

- **baba_agent_sdk.py**: Main agent using Claude Code SDK
  - Configures MCP server connection
  - Sets up Claude with appropriate prompts
  - Handles game session management
  
- **test_connection.py**: MCP connection tester
  - Verifies MCP server is accessible
  - Tests basic game operations

### How It Works

1. **MCP Server Launch**: The agent automatically starts the MCP server as a subprocess
2. **Claude Integration**: Uses Claude Code SDK to connect to Claude API
3. **Game Analysis**: Claude analyzes the game state and identifies:
   - Active rules (e.g., "BABA IS YOU", "FLAG IS WIN")
   - Controlled objects
   - Win conditions
   - Possible rule modifications
4. **Strategic Execution**: Claude executes moves to solve puzzles

### Configuration

The agent reads configuration from `config.toml`:
- `agent.max_turns`: Maximum turns Claude can take (default: 50)
- `agent.default_level`: Default level to play if not specified
- `agent.verbose`: Whether to show detailed output

## Standalone Usage

If you want to run the agent directly without the orchestration script:

```bash
cd agent
python baba_agent_sdk.py 1  # Play level 1
```

## Development

### Modifying the Agent Prompt

Edit the prompt in `baba_agent_sdk.py` to change how Claude approaches the game. The prompt includes:
- Game mechanics explanation
- Available tools documentation
- Strategic guidance

### Testing MCP Connection

```bash
cd agent
python test_connection.py
```

This will:
1. Connect to the MCP server
2. List available tools
3. Test basic operations

## Troubleshooting

- **MCP Connection Failed**: Ensure the game is running and a level is loaded
- **No Game State**: The game must be focused and in a level
- **API Key Error**: Set your ANTHROPIC_API_KEY environment variable
- **Module Import Errors**: Run `pixi install` from the root directory