#!/usr/bin/env python3
"""Orchestration script to run Baba Is You with MCP server and agent."""

import os
import sys
import subprocess
import time
import signal
import psutil
import toml
from pathlib import Path
import argparse

def load_config():
    """Load configuration file."""
    config_path = Path(__file__).parent.parent / "config.toml"
    if not config_path.exists():
        print("Error: config.toml not found. Please run 'pixi run setup' first.")
        sys.exit(1)
    
    with open(config_path, "r") as f:
        return toml.load(f)

def find_baba_executable(game_path):
    """Find the Baba Is You executable."""
    possible_names = ["Baba Is You", "BabaIsYou", "Baba Is You.exe", "BabaIsYou.exe"]
    
    for name in possible_names:
        exe_path = game_path / name
        if exe_path.exists():
            return exe_path
    
    # Check in Contents/MacOS for macOS apps
    macos_path = game_path / "Contents" / "MacOS" / "Baba Is You"
    if macos_path.exists():
        return macos_path
    
    print(f"Error: Could not find Baba Is You executable in {game_path}")
    sys.exit(1)

def start_game(game_path):
    """Start Baba Is You game."""
    exe_path = find_baba_executable(game_path)
    print(f"Starting Baba Is You from: {exe_path}")
    
    # Start the game in background
    if sys.platform == "darwin":  # macOS
        subprocess.Popen(["open", str(exe_path.parent.parent)])
    else:
        subprocess.Popen([str(exe_path)])
    
    # Wait for game to start
    print("Waiting for game to start...")
    time.sleep(5)

def start_mcp_server(config):
    """Start the MCP server."""
    # Path to game_mcp.py
    mcp_script = Path(__file__).parent.parent / "baba_is_eval" / "game_mcp.py"
    
    print("Starting MCP server...")
    process = subprocess.Popen(
        [sys.executable, str(mcp_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"MCP server failed to start:")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        sys.exit(1)
    
    print(f"MCP server started (PID: {process.pid})")
    return process

def start_agent(level_id, config):
    """Start the agent to play the specified level."""
    agent_script = Path(__file__).parent.parent / "agent" / "baba_agent_sdk.py"
    
    print(f"Starting agent to play level {level_id}...")
    process = subprocess.Popen(
        [sys.executable, str(agent_script), str(level_id)]
    )
    
    return process

def cleanup_processes(processes):
    """Clean up all started processes."""
    print("\nCleaning up processes...")
    for name, process in processes.items():
        if process and process.poll() is None:
            print(f"Terminating {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()

def main():
    parser = argparse.ArgumentParser(description="Play Baba Is You with AI agent")
    parser.add_argument("level", nargs="?", help="Level ID to play (e.g., 1, 2, 3)")
    parser.add_argument("--no-game", action="store_true", help="Don't start the game (assume it's already running)")
    parser.add_argument("--mcp-only", action="store_true", help="Only start MCP server")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    game_path = Path(config["game"]["path"])
    
    # Use default level if not specified
    level_id = args.level or config["agent"].get("default_level", "1")
    
    processes = {}
    
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal")
        cleanup_processes(processes)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start game if needed
        if not args.no_game and not args.mcp_only:
            start_game(game_path)
        
        # Start MCP server
        mcp_process = start_mcp_server(config)
        processes["MCP Server"] = mcp_process
        
        if args.mcp_only:
            print("MCP server is running. Press Ctrl+C to stop.")
            mcp_process.wait()
        else:
            # Start agent
            agent_process = start_agent(level_id, config)
            processes["Agent"] = agent_process
            
            print(f"\nAgent is playing level {level_id}...")
            print("Press Ctrl+C to stop.\n")
            
            # Wait for agent to complete or be interrupted
            agent_process.wait()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup_processes(processes)

if __name__ == "__main__":
    main()