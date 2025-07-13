#!/bin/bash

# Baba Is Eval Setup
set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in the baba_is_eval directory
if [[ ! -f "$SCRIPT_DIR/game_mcp.py" ]]; then
    echo "Error: This script must be run from the baba_is_eval directory"
    echo "Please navigate to the baba_is_eval folder and run this script again"
    exit 1
fi

# Assume we're already in the Data directory
BABA_DATA_DIR="$(pwd)"
LUA_DIR="$BABA_DATA_DIR/Lua"

# Check if the Lua directory exists
if [[ ! -d "$LUA_DIR" ]]; then
    echo "Error: Lua directory not found at $LUA_DIR"
    echo "Please ensure this script is run from the Baba Is You Data directory"
    exit 1
fi

echo "Setting up modification..."

# Clear the commands directory
echo "Clearing commands directory..."
if [[ -d "$SCRIPT_DIR/commands" ]]; then
    rm -rf "$SCRIPT_DIR/commands"/*
    echo "✓ Commands directory cleared"
else
    echo "Warning: Commands directory not found, creating it..."
    mkdir -p "$SCRIPT_DIR/commands"
fi

# Copy io.lua to the Lua directory
echo "Copying io.lua to Lua directory..."
if [[ -f "$SCRIPT_DIR/io.lua" ]]; then
    cp "$SCRIPT_DIR/io.lua" "$LUA_DIR/"
    echo "✓ io.lua copied to $LUA_DIR/"
else
    echo "Error: io.lua not found in $SCRIPT_DIR"
    exit 1
fi

echo "✓ Setup completed successfully!"