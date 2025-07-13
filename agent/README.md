# Baba Is You AI Agent

An autonomous agent that plays Baba Is You using Claude AI and the MCP (Model Control Protocol) server.

## Features

- **Autonomous Gameplay**: The agent analyzes game states and makes decisions using Claude AI
- **MCP Integration**: Communicates with Baba Is You through the MCP server interface
- **Game State Analysis**: Understands rules, win conditions, and possible moves
- **Strategic Planning**: Plans moves to achieve level objectives

## Prerequisites

1. **Baba Is You Game**: Purchase and install from Steam
2. **Python 3.11+**: Required for the agent
3. **Anthropic API Key**: Set as `ANTHROPIC_API_KEY` environment variable
4. **Pixi**: For Python environment management

## Setup

1. **Game Setup**:
   ```bash
   # Navigate to the game's Data folder and clone baba_is_eval there
   # Run the setup script
   cd baba_is_eval
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Agent Setup**:
   ```bash
   # Install pixi dependencies
   cd baba_agent
   pixi install
   
   # Set your Anthropic API key
   export ANTHROPIC_API_KEY="your-key-here"
   ```

## Usage

### Method 1: Run MCP Server Separately

1. Start the MCP server:
   ```bash
   cd baba_is_eval
   mcp dev game_mcp.py
   ```

2. In another terminal, run the agent:
   ```bash
   cd baba_agent
   pixi run python baba_agent.py
   ```

### Method 2: Agent Launches MCP Server

The agent can also launch the MCP server automatically:
```bash
cd baba_agent
pixi run python baba_agent.py
```

### Testing Connection

To test if everything is set up correctly:
```bash
pixi run python test_connection.py
```

## How It Works

1. **Game State Reading**: The MCP server reads the game state through modded Lua functions
2. **State Analysis**: Claude analyzes the game board, identifying:
   - Active rules (e.g., "BABA IS YOU", "FLAG IS WIN")
   - Controlled objects
   - Win conditions
   - Possible rule changes
3. **Move Planning**: Claude recommends movement commands based on the analysis
4. **Execution**: The agent sends commands through MCP to control the game

## Agent Architecture

- `BabaIsYouAgent`: Main agent class
  - Connects to MCP server
  - Manages game state
  - Interfaces with Claude AI
  - Executes game commands

- Key Methods:
  - `connect_to_mcp()`: Establishes MCP connection
  - `analyze_game_state_with_claude()`: Gets AI analysis
  - `play_level_autonomously()`: Plays a level without human intervention

## Troubleshooting

- **MCP Connection Failed**: Ensure the game is running and focused
- **No Game State**: Run setup.sh again and restart the game
- **API Key Error**: Set your ANTHROPIC_API_KEY environment variable
- **Game Not Responding**: Click on the game window to focus it