# Baba Is Eval

https://github.com/user-attachments/assets/cb6d0d49-b583-46a2-b262-1cf38279a531

We evaluate language models' meta-level reasoning in an interactive setting, like the upcoming ARC-AGI-3, except we use the brilliant puzzle game "Baba Is You". In short, the player manipulates the game rules by pushing word blocks around to form or destroy rules. We provide an MCP server to interact with the game in text format. The project is currently an alpha and not stable. Contributions are welcome, and brave devs with model credits to spare are invited to give it a try.

## Setup 🔩

- Buy "Baba Is You" somewhere, like on Steam: https://store.steampowered.com/app/736260/Baba_Is_You
- Clone this repo in the `Data` folder
   - macOS + Steam: `/Users/[username]/Library/Application Support/Steam/steamapps/common/Baba Is You/Baba Is You.app/Contents/Resources/Data`
   - Windows + Steam (?): `C:\Program Files (x86)\Steam\steamapps\common\Baba Is You\Data`
- Install prerequisites (or use `uv`)
```bash
pip install mcp fastmcp pyautogui configparser
```
- Run the setup script (after inspecting its contents) (also required before restarting the game, and for changes to `io.lua` which in turn require restarting the game)
```bash
cd baba_is_eval
chmod +x setup.sh
./setup.sh
```
- Open the game, preferably in a command line
   - macOS + Steam: `/Users/[username]/Library/Application Support/Steam/steamapps/common/Baba Is You/Baba Is You.app/Contents/MacOS/Chowdren`
   - (Currently we use clicking as a workaround for focusing, you might need to move the window to (800, 500) pixels on monitor one)
- Start the MCP Server
```bash
mcp dev baba_is_eval/game_mcp.py
```

On top of this MCP client agnostic setup, you can use a client like Claude Desktop to have a model interact with the server and play the game.

### Available MCP Tools

The server provides these tools for interacting with the game:

- **`enter_level(level: str)`** - Enter a specific level (e.g., "1", "2", "3")
- **`get_game_state()`** - Get the current game state as a matrix
- **`execute_commands(commands: str)`** - Execute movement commands (e.g., "right,up,down")
- **`undo_multiple(n: int)`** - Undo the last n moves
- **`restart_level()`** - Restart the current level
- **`leave_level()`** - Exit the current level
- **`game_rules(topic: str)`** - Get help on game rules

The game state is returned as a matrix like this:
```
y/x |  1  |  2  |  3  |  4  |  5  
----+-----+-----+-----+-----+-----
 1  |     |     |     |     |     
 2  |     | baba|     |     |     
 3  |     |     | flag|     |     
 4  |     |     |     |     |     
 5  |     |     |     |     |     
```

## Roadmap 🛣️

Contributions welcome! Goals listed in order of pressingness.

- [x] Reading and writing using modded Lua
- [x] MCP integration
- [ ] Acceptable game I/O reliability
- [ ] Complete MCP control over game functionality
- [ ] Automated evaluation logs
- [ ] More efficient scaffolding
- [ ] Menu navigation beyond the first 8 levels, to arbitrary levels
- [ ] Good latency
- [ ] Parallel execution
- [ ] Support for community levels


## Inner Workings ⚰️

This works in the dumbest way possible; we reverse engineer the exposed Lua functions, use the mod functionality to read the game state, and write to one of the game state config files using mod hooks, which is then read in by the MCP server. For move and undo inputs, we write Lua files to `commands/` from the MCP server to be read in, if detected, in the `always` mod hook. Perhaps this dooms the project to be brittle and slow forever, but perhaps there is some better way. 


## Credits
Baba is You was created by Hempuli. It is a lovely game, go play it yourself!
