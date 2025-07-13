from mcp.server.fastmcp import FastMCP
import os
import configparser
import pyautogui
import time
import json
import toml
from pathlib import Path

# Load configuration
config_path = Path(__file__).parent.parent / "config.toml"
if config_path.exists():
    with open(config_path, "r") as f:
        config = toml.load(f)
    GAME_PATH = config["game"]["path"]
else:
    # Fallback to relative path
    GAME_PATH = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(GAME_PATH, "Data") if "Data" not in GAME_PATH else GAME_PATH

STATE_PATH = os.path.join(DATA_PATH, "Worlds", "baba", "world_data.txt")
COMMANDS_DIR = os.path.join(DATA_PATH, "baba_is_eval", "commands")
HELP_RULES_PATH = os.path.join(DATA_PATH, "baba_is_eval", "help_rules.json")

# State tracking for last entered level/world
last_level = None
last_world = None
current_level_moves = []  # Track movement sequence for current level


def click_to_focus_game():
    """Click on game window to focus it"""
    pyautogui.click(800, 500)
    return False


def reverse_movement_commands(commands):
    """Reverse a list of movement commands to backtrack."""
    reverse_map = {"right": "left", "left": "right", "up": "down", "down": "up"}
    # Reverse the list and map each command to its opposite
    return [reverse_map.get(cmd, cmd) for cmd in reversed(commands)]


def get_next_command_file():
    k = 0
    while True:
        path = os.path.join(COMMANDS_DIR, f"{k}.lua")
        if not os.path.exists(path):
            return path
        k += 1


def write_command_sequence(commands):
    """Write a sequence of movement commands to the command file."""
    command_file = get_next_command_file()
    with open(command_file, "w", encoding="utf-8") as f:
        f.write("\n".join([f'command("{cmd}",1)' for cmd in commands]) + "\n")
    return command_file


def execute_control_file_and_wait(command_file_path, max_wait_time=10):
    """Write commands to a control file and wait for processing, returning the new game state."""
    command_file_number = int(os.path.basename(command_file_path).split(".")[0])
    print(f"Writing commands to {command_file_path}")

    # Wait for the command file to be processed
    wait_interval = 0.1
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        try:
            config = configparser.ConfigParser()
            config.read(STATE_PATH, encoding="utf-8")

            # Check if the command file has been processed
            if "file" in config and "last_processed" in config["file"]:
                last_processed = int(config["file"]["last_processed"])
                if last_processed >= command_file_number:
                    # Command has been processed, return the new game state
                    return get_game_state()

            time.sleep(wait_interval)
        except Exception:
            # If there's an error reading the config, continue waiting
            time.sleep(wait_interval)

    # If we've waited too long, return the current state anyway
    return get_game_state()


def _enter_level(level: str, world: str = "top"):
    click_to_focus_game()
    global last_level, last_world, current_level_moves
    sequence = []
    if world == "top":
        if level.isnumeric():
            level_num = int(level)
            if level_num >= 1:
                sequence += ["right", "up", "up"]
            level_moves = {
                2: ["up"],
                3: ["right"],
                4: ["up", "right"],
                5: ["up", "up"],
                6: ["up", "right", "right"],
                7: ["up", "up", "right"],
            }
            if level_num in level_moves:
                sequence += level_moves[level_num]
    # Separate movement and non-movement commands
    movement_cmds = [cmd for cmd in sequence if cmd in COMMAND_LIST]
    # Store the movement sequence for later reversal
    current_level_moves = movement_cmds.copy()
    if movement_cmds:
        write_command_sequence(movement_cmds)

    # For entering, use pyautogui directly with retry logic
    time.sleep(1)
    level_entered = False
    for attempt in range(2):
        print(f"Enter attempt {attempt + 1}/2")

        # Try the enter sequence
        for _ in range(3):
            pyautogui.press("enter")

        # Wait for the level to potentially load
        time.sleep(1)

    level_entered = True

    # If level entry was successful, write level_won as false
    if level_entered:
        config = configparser.ConfigParser()
        config.read(STATE_PATH, encoding="utf-8")

        # Set level_won to false
        config["status"]["level_won"] = "false"

        # Write the updated config back to the file
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            config.write(f)

    last_level = level
    last_world = world
    return f"Entered level {level}."


# Create an MCP server
mcp = FastMCP("Baba is Eval")

# Command mapping (reused from io.py)
COMMAND_LIST = [
    "right",
    "up",
    "left",
    "down",
    "idle",
    "undo",
    "quit",
    "restart_instant",
]


def read_world_state():
    config = configparser.ConfigParser()
    config.read(STATE_PATH, encoding="utf-8")

    # Get the state section and parse the units
    state_data = config["state"]["state"]
    # Each unit is separated by '€', each field by '|'
    units = [unit.split("|") for unit in state_data.split("€") if unit]

    # Convert the raw data into a list of dictionaries with proper field names
    parsed_units = []
    for unit in units:
        if len(unit) >= 21:  # Ensure we have all required fields
            parsed_unit = {
                "key": unit[0],
                "UNITNAME": unit[1],
                "UNITTYPE": unit[2],
                "XPOS": unit[3],
                "YPOS": unit[4],
                "DIR": unit[5],
                "VISUALDIR": unit[6],
                "ZLAYER": unit[7],
                "MOVED": unit[8],
                "EFFECT": unit[9],
                "COLOUR": unit[10],
                "VISUALSTYLE": unit[11],
                "VISUALLEVEL": unit[12],
                "CLEARCOLOUR": unit[13],
                "DECOR": unit[14],
                "ONLINE": unit[15],
                "COMPLETED": unit[16],
                "EFFECTCOUNT": unit[17],
                "FLOAT": unit[18],
                "A": unit[19],
                "ID": unit[20],
            }
            parsed_units.append(parsed_unit)

    # Read room size information
    room_size = None
    try:
        room_size_data = config["state"]["room_size"]
        room_size_parts = room_size_data.split("|")
        if len(room_size_parts) == 2:
            room_size = (int(room_size_parts[0]), int(room_size_parts[1]))
    except (KeyError, ValueError):
        # If room size is not available, we'll compute it from units
        pass

    return parsed_units, room_size


@mcp.tool()
def game_rules(topic: str = "basic") -> str:
    """Get help on Baba Is You game rules. Use 'basic' for general rules, or specify a word like 'stop' for specific rule explanations."""
    try:
        # Read the help rules from JSON file
        with open(HELP_RULES_PATH, "r", encoding="utf-8") as f:
            rules_data = json.load(f)

        # Get the requested topic (default to basic if not found)
        topic_key = topic.lower()
        if topic_key not in rules_data:
            available_topics = ", ".join(rules_data.keys())
            return f"Unknown topic '{topic}'. Available topics are: {available_topics}"

        rule_info = rules_data[topic_key]
        return f"{rule_info['title']}\n\n{rule_info['content']}"

    except FileNotFoundError:
        return f"Help rules file not found at {HELP_RULES_PATH}"
    except json.JSONDecodeError:
        return "Error reading help rules file: invalid JSON format"
    except Exception as e:
        return f"Error reading help rules: {str(e)}"


@mcp.tool()
def enter_level(level: str) -> str:
    """Enter a level."""
    return _enter_level(level, "top")


@mcp.tool()
def get_game_state() -> str:
    """Prints the game state as a matrix, with each cell showing the game entity's name, separated by z-layer if multiple."""
    try:
        units, room_size = read_world_state()
        # Filter out unwanted units
        # units = [u for u in units if u['UNITNAME'] not in ['line', 'cursor']]
        # Convert positions to int for sorting
        for u in units:
            u["XPOS"] = int(u["XPOS"])
            u["YPOS"] = int(u["YPOS"])
            u["ZLAYER"] = int(u["ZLAYER"])

        # Use room size for bounding box if available, otherwise compute from units
        if room_size is not None:
            min_x, min_y = 1, 1  # Trim one space from each edge
            max_x, max_y = room_size[0] - 2, room_size[1] - 2
        else:
            if not units:
                return "No units found and no room size available."
            # Compute bounding box from units (fallback)
            min_x = min(u["XPOS"] for u in units)
            max_x = max(u["XPOS"] for u in units)
            min_y = min(u["YPOS"] for u in units)
            max_y = max(u["YPOS"] for u in units)
            # Trim one space from each edge
            min_x += 1
            max_x -= 1
            min_y += 1
            max_y -= 1

        # Build a map: (x, y) -> list of (z, name)
        pos_map = {}
        for u in units:
            key = (u["XPOS"], u["YPOS"])
            if key not in pos_map:
                pos_map[key] = []
            pos_map[key].append((u["ZLAYER"], u["UNITNAME"]))
        # Sort the z-layers for each cell
        for v in pos_map.values():
            v.sort()

        # Compute width for first column (y-coordinates)
        first_col_width = max(
            len("y/x"), max(len(str(y)) for y in range(min_y, max_y + 1)), 3
        )

        # Compute max width for each column (x)
        col_widths = {}
        for x in range(min_x, max_x + 1):
            maxlen = 0
            for y in range(min_y, max_y + 1):
                cell = pos_map.get((x, y), [])
                if len(cell) > 1:
                    # Format stacked objects as z1<z2<z99
                    cell_content = "<".join([f"{name}" for z, name in cell])
                elif len(cell) == 1:
                    cell_content = cell[0][1]  # Just the name
                else:
                    cell_content = ""
                
                if len(cell_content) > maxlen:
                    maxlen = len(cell_content)
            col_widths[x] = max(maxlen, 5)  # At least 5 chars wide

        # Build the matrix rows
        lines = []
        # Header row
        header = ["y/x".ljust(first_col_width)] + [
            f"{x}".center(col_widths[x]) for x in range(min_x, max_x + 1)
        ]
        lines.append(" | ".join(header))
        lines.append(
            "-" * first_col_width
            + "-+-"
            + "-+-".join(["-" * col_widths[x] for x in range(min_x, max_x + 1)])
        )
        
        # Print each row
        for y in range(min_y, max_y + 1):
            row = [f"{y}".ljust(first_col_width)]
            for x in range(min_x, max_x + 1):
                cell = pos_map.get((x, y), [])
                if len(cell) > 1:
                    # Format stacked objects as z1<z2<z99
                    cell_content = "<".join([f"{name}" for z, name in cell])
                elif len(cell) == 1:
                    cell_content = cell[0][1]  # Just the name
                else:
                    cell_content = ""
                row.append(cell_content.ljust(col_widths[x]))
            lines.append(" | ".join(row))
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def execute_commands(commands: str) -> str:
    """Execute a sequence of commands.
    Commands should be a comma-separated list of command names (e.g. 'right,up,down')."""
    try:
        # Split and validate commands
        command_list = [cmd.strip() for cmd in commands.split(",")]
        valid_commands = []

        for cmd in command_list:
            if cmd in COMMAND_LIST:
                valid_commands.append(cmd)
            else:
                return f"Invalid command: {cmd}. Valid commands are: {', '.join(COMMAND_LIST)}"

        if not valid_commands:
            return "No valid commands provided"

        # Write commands to file
        command_file = get_next_command_file()
        with open(command_file, "w", encoding="utf-8") as f:
            f.write("\n".join([f'command("{cmd}",1)' for cmd in valid_commands]) + "\n")

        # Check if level was won by reading the level_won status
        level_won_status = "unknown"

        config = configparser.ConfigParser()
        config.read(STATE_PATH, encoding="utf-8")
        level_won_status = config["status"]["level_won"]

        # Add level won status to the response
        if level_won_status == "true":
            return "Level won! You can now enter another level to earn more points."
        else:
            return "Commands executed successfully. You have not yet won the level, please continue."

    except Exception as e:
        return f"Error executing commands: {str(e)}"


@mcp.tool()
def undo_multiple(n: int) -> str:
    """Undo the last n moves by creating a control file with n undo() commands."""
    try:
        print(f"Undoing {n} moves")
        if n <= 0:
            return "Number of undos must be positive"

        # Create control file with n undo commands
        command_file = get_next_command_file()
        with open(command_file, "w", encoding="utf-8") as f:
            f.write("\n".join(["undo()" for _ in range(n)]) + "\n")

        print(f"Created control file with {n} undo commands")
        return execute_control_file_and_wait(command_file)
    except Exception as e:
        return f"Error undoing moves: {str(e)}"


@mcp.tool()
def restart_level() -> str:
    """Restarts the current level."""
    try:
        click_to_focus_game()
        pyautogui.press("r")
        return "Restarted the current level"
    except Exception as e:
        return f"Error restarting level: {str(e)}"


@mcp.tool()
def leave_level() -> str:
    """Exits the current level."""
    global current_level_moves
    try:
        click_to_focus_game()

        # Get initial world state
        initial_state = get_game_state()

        max_attempts = 5
        for attempt in range(max_attempts):
            print(f"Exit attempt {attempt + 1}/{max_attempts}")

            # Try the exit sequence
            pyautogui.press("escape")
            time.sleep(0.1)
            pyautogui.press("down")
            time.sleep(0.1)
            pyautogui.press("enter")

            # Wait for the level to potentially exit
            time.sleep(1)

            # Check if the world state has changed
            current_state = get_game_state()

            if current_state != initial_state:
                print("World state changed - level exit successful")
                break
            else:
                print("World state unchanged - level exit failed, retrying...")
                if attempt < max_attempts - 1:
                    time.sleep(0.5)  # Wait a bit before retry

        # Reverse the movement sequence to return to initial position
        if current_level_moves:
            reverse_commands = reverse_movement_commands(current_level_moves)
            print(
                f"Reversing movement sequence: {current_level_moves} -> {reverse_commands}"
            )
            write_command_sequence(reverse_commands)
            # Clear the stored movement sequence
            current_level_moves = []
            return f"Left level and returned to initial position by reversing {len(reverse_commands)} moves."
        else:
            return "Left level (no movement sequence to reverse)."
    except Exception as e:
        return f"Error leaving level: {str(e)}"


if __name__ == "__main__":
    click_to_focus_game()
    mcp.run()
