#!/usr/bin/env python3
"""Setup script to prepare Baba Is You for MCP integration."""

import os
import sys
import subprocess
import platform
import toml
from pathlib import Path

def find_baba_installation():
    """Find Baba Is You installation directory."""
    system = platform.system()
    
    possible_paths = []
    
    if system == "Darwin":  # macOS
        possible_paths = [
            Path.home() / "Library/Application Support/Steam/steamapps/common/Baba Is You",
            Path("/Applications/Baba Is You.app"),
        ]
    elif system == "Windows":
        possible_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Baba Is You"),
            Path("C:/Program Files/Steam/steamapps/common/Baba Is You"),
        ]
    elif system == "Linux":
        possible_paths = [
            Path.home() / ".steam/steam/steamapps/common/Baba Is You",
            Path.home() / ".local/share/Steam/steamapps/common/Baba Is You",
        ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # If not found, prompt user
    print("Could not automatically find Baba Is You installation.")
    custom_path = input("Please enter the full path to your Baba Is You installation: ")
    return Path(custom_path)

def setup_baba_is_eval(game_path):
    """Set up the baba_is_eval mod in the game directory."""
    data_path = game_path / "Data"
    if not data_path.exists():
        print(f"Error: Data directory not found at {data_path}")
        return False
    
    # Check if setup is already done
    io_lua_path = data_path / "io.lua"
    if io_lua_path.exists():
        print("Setup appears to be already complete (io.lua exists)")
        return True
    
    # Copy necessary files
    eval_path = Path(__file__).parent.parent / "baba_is_eval"
    
    # Copy io.lua to Data directory
    io_lua_src = eval_path / "io.lua"
    if io_lua_src.exists():
        print(f"Copying io.lua to {data_path}")
        subprocess.run(["cp", str(io_lua_src), str(data_path)], check=True)
    
    # Create necessary directories
    worlds_baba_path = data_path / "Worlds" / "baba"
    worlds_baba_path.mkdir(parents=True, exist_ok=True)
    
    commands_path = data_path / "baba_is_eval" / "commands"
    commands_path.mkdir(parents=True, exist_ok=True)
    
    # Copy help_rules.json
    help_rules_src = eval_path / "help_rules.json"
    help_rules_dst = data_path / "baba_is_eval" / "help_rules.json"
    if help_rules_src.exists():
        print(f"Copying help_rules.json to {help_rules_dst}")
        subprocess.run(["cp", str(help_rules_src), str(help_rules_dst)], check=True)
    
    print("Setup complete!")
    return True

def update_config(game_path):
    """Update the config file with the detected game path."""
    config_path = Path(__file__).parent.parent / "config.toml"
    
    # Load existing config
    if config_path.exists():
        with open(config_path, "r") as f:
            config = toml.load(f)
    else:
        config = {"game": {}, "mcp": {}, "agent": {}}
    
    # Update game path
    config["game"]["path"] = str(game_path)
    
    # Write back
    with open(config_path, "w") as f:
        toml.dump(config, f)
    
    print(f"Updated config file at {config_path}")

def main():
    print("Setting up Baba Is You for MCP integration...")
    
    # Find game installation
    game_path = find_baba_installation()
    if not game_path.exists():
        print(f"Error: Game path {game_path} does not exist")
        sys.exit(1)
    
    print(f"Found Baba Is You at: {game_path}")
    
    # Update config file
    update_config(game_path)
    
    # Setup baba_is_eval
    if not setup_baba_is_eval(game_path):
        print("Setup failed!")
        sys.exit(1)
    
    print("\nSetup complete! You can now run: pixi run play <level_id>")

if __name__ == "__main__":
    main()