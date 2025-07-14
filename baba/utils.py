"""Utility functions for Baba Is You."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .grid import Grid
from .registration import Registry
from .properties import Property


def save_state(grid: Grid, filepath: str):
    """
    Save the current game state to a file.

    Args:
        grid: The game grid to save
        filepath: Path to save the state
    """
    state = {
        "width": grid.width,
        "height": grid.height,
        "steps": grid.steps,
        "won": grid.won,
        "lost": grid.lost,
        "objects": []
    }
    
    # Save all objects
    for y in range(grid.height):
        for x in range(grid.width):
            for obj in grid.grid[y][x]:
                obj_data = {
                    "x": x,
                    "y": y,
                    "name": obj.name,
                    "type_id": obj.type_id,
                    "is_text": obj.is_text
                }
                state["objects"].append(obj_data)
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(state, f, indent=2)


def load_state(filepath: str, registry: Registry) -> Optional[Grid]:
    """
    Load a game state from a file.

    Args:
        filepath: Path to load the state from
        registry: Object registry to use

    Returns:
        Loaded grid or None if failed
    """
    try:
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Create grid
        grid = Grid(state["width"], state["height"], registry)
        grid.steps = state["steps"]
        grid.won = state["won"]
        grid.lost = state["lost"]
        
        # Load objects
        for obj_data in state["objects"]:
            name = obj_data["name"]
            is_text = obj_data["is_text"]
            
            # Create object instance
            if is_text:
                # Remove "_text" suffix if present
                if name.endswith("_text"):
                    name = name[:-5]
                obj = registry.create_instance(name, is_text=True)
            else:
                obj = registry.create_instance(name, is_text=False)
            
            if obj:
                grid.place_object(obj, obj_data["x"], obj_data["y"])
        
        # Update rules
        grid._update_rules()
        
        return grid
    
    except Exception as e:
        print(f"Failed to load state: {e}")
        return None


def create_level_from_string(level_str: str, registry: Registry) -> Grid:
    """
    Create a level from a string representation.

    Args:
        level_str: String representation of the level
        registry: Object registry

    Returns:
        Created grid

    The string format uses characters to represent objects:
    - 'B' = Baba
    - 'W' = Wall
    - 'R' = Rock
    - 'F' = Flag
    - 'A' = Water
    - 'b' = BABA text
    - 'w' = WALL text
    - 'r' = ROCK text
    - 'f' = FLAG text
    - 'a' = WATER text
    - 'i' = IS text
    - 'y' = YOU text
    - 'n' = WIN text
    - 's' = STOP text
    - 'p' = PUSH text
    - 'k' = SINK text
    - '.' = Empty space
    """
    lines = level_str.strip().split('\n')
    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0
    
    grid = Grid(width, height, registry)
    
    # Character to object mapping
    char_map = {
        # Game objects
        'B': ('baba', False),
        'W': ('wall', False),
        'R': ('rock', False),
        'F': ('flag', False),
        'A': ('water', False),
        # Text objects
        'b': ('baba', True),
        'w': ('wall', True),
        'r': ('rock', True),
        'f': ('flag', True),
        'a': ('water', True),
        'i': ('is', True),
        'y': ('you', True),
        'n': ('win', True),
        's': ('stop', True),
        'p': ('push', True),
        'k': ('sink', True),
    }
    
    # Parse the level
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char in char_map:
                name, is_text = char_map[char]
                obj = registry.create_instance(name, is_text)
                if obj:
                    grid.place_object(obj, x, y)
    
    # Update rules
    grid._update_rules()
    
    return grid


def export_level_to_string(grid: Grid) -> str:
    """
    Export a level to string representation.

    Args:
        grid: Grid to export

    Returns:
        String representation of the level
    """
    # Object to character mapping (reverse of char_map above)
    obj_map = {
        # Game objects
        ('baba', False): 'B',
        ('wall', False): 'W',
        ('rock', False): 'R',
        ('flag', False): 'F',
        ('water', False): 'A',
        # Text objects
        ('baba_text', True): 'b',
        ('wall_text', True): 'w',
        ('rock_text', True): 'r',
        ('flag_text', True): 'f',
        ('water_text', True): 'a',
        ('is_text', True): 'i',
        ('you_text', True): 'y',
        ('win_text', True): 'n',
        ('stop_text', True): 's',
        ('push_text', True): 'p',
        ('sink_text', True): 'k',
    }
    
    lines = []
    for y in range(grid.height):
        line = []
        for x in range(grid.width):
            objects = grid.grid[y][x]
            if objects:
                # Get the first object (prioritize text objects)
                obj = max(objects, key=lambda o: (o.is_text, o.type_id))
                key = (obj.name, obj.is_text)
                char = obj_map.get(key, '?')
                line.append(char)
            else:
                line.append('.')
        lines.append(''.join(line))
    
    return '\n'.join(lines)


def get_valid_actions() -> List[str]:
    """Get the list of valid actions."""
    return ['up', 'down', 'left', 'right', 'wait']


def action_to_delta(action: str) -> Tuple[int, int]:
    """
    Convert an action to a (dx, dy) delta.

    Args:
        action: Action string

    Returns:
        (dx, dy) tuple
    """
    deltas = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
        'wait': (0, 0)
    }
    return deltas.get(action, (0, 0))


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two positions.

    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)

    Returns:
        Manhattan distance
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def find_path(
    grid: Grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    avoid_objects: Optional[List[str]] = None
) -> Optional[List[Tuple[int, int]]]:
    """
    Find a path from start to goal using A*.

    Args:
        grid: Game grid
        start: Starting position
        goal: Goal position
        avoid_objects: List of object names to avoid

    Returns:
        List of positions forming the path, or None if no path exists
    """
    from heapq import heappush, heappop
    
    if avoid_objects is None:
        avoid_objects = []
    
    # Check if position is walkable
    def is_walkable(x: int, y: int) -> bool:
        if not (0 <= x < grid.width and 0 <= y < grid.height):
            return False
        
        objects = grid.get_objects_at(x, y)
        for obj in objects:
            # Check if object should be avoided
            if obj.name in avoid_objects:
                return False
            # Check if object has STOP property
            if grid.rule_manager.has_property(obj.name, Property.STOP):
                return False
        
        return True
    
    # A* implementation
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    
    while open_set:
        current = heappop(open_set)[1]
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return list(reversed(path))
        
        # Check neighbors
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if not is_walkable(*neighbor):
                continue
            
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + manhattan_distance(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))
    
    return None


def count_objects(grid: Grid) -> Dict[str, int]:
    """
    Count all objects in the grid by type.

    Args:
        grid: Game grid

    Returns:
        Dictionary mapping object names to counts
    """
    counts = {}
    
    for y in range(grid.height):
        for x in range(grid.width):
            for obj in grid.grid[y][x]:
                name = obj.name
                counts[name] = counts.get(name, 0) + 1
    
    return counts


def visualize_rules(grid: Grid) -> str:
    """
    Create a text visualization of active rules.

    Args:
        grid: Game grid

    Returns:
        String representation of rules
    """
    rules = grid.rule_manager.rules
    
    if not rules:
        return "No active rules"
    
    lines = ["Active Rules:"]
    for rule in rules:
        lines.append(f"  - {rule}")
    
    # Add derived properties
    lines.append("\nObject Properties:")
    for obj_name, props in grid.rule_manager.properties.items():
        prop_str = ", ".join(prop.value for prop in props)
        lines.append(f"  - {obj_name}: {prop_str}")
    
    # Add transformations
    if grid.rule_manager.transformations:
        lines.append("\nTransformations:")
        for from_obj, to_obj in grid.rule_manager.transformations.items():
            lines.append(f"  - {from_obj} → {to_obj}")
    
    return "\n".join(lines)