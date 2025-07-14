"""Fun and unique sprite generation for Baba Is You objects."""

import numpy as np
import cv2
from typing import Tuple, Dict, List


def create_sprite_from_pattern(
    pattern: List[str], 
    fg_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int] = (0, 0, 0),
    size: Tuple[int, int] = (24, 24)
) -> np.ndarray:
    """
    Create a sprite from an ASCII pattern.
    
    Args:
        pattern: List of strings representing the sprite pattern
        fg_color: Foreground (character) color
        bg_color: Background color
        size: Output size
    
    Returns:
        Sprite as numpy array
    """
    # Create sprite at pattern resolution
    height = len(pattern)
    width = max(len(row) for row in pattern) if pattern else 1
    
    sprite = np.full((height, width, 3), bg_color, dtype=np.uint8)
    
    # Fill in the pattern
    for y, row in enumerate(pattern):
        for x, char in enumerate(row):
            if char != ' ' and char != '.':
                sprite[y, x] = fg_color
    
    # Resize to target size
    sprite = cv2.resize(sprite, size, interpolation=cv2.INTER_NEAREST)
    
    return sprite


# Sprite patterns for game objects
SPRITE_PATTERNS = {
    # Baba - cute creature with ears
    "baba": [
        "  ▲▲  ",
        " ████ ",
        "██●●██",
        "██████",
        " ████ ",
        "██  ██"
    ],
    
    # Wall - brick pattern
    "wall": [
        "██████",
        "██████",
        "──────",
        "██████",
        "██████",
        "──────"
    ],
    
    # Rock - rough circular shape
    "rock": [
        " ████ ",
        "██████",
        "██████",
        "██████",
        "██████",
        " ████ "
    ],
    
    # Flag - waving flag
    "flag": [
        "█▀▀▀▀ ",
        "█████ ",
        "█▄▄▄▄ ",
        "  █   ",
        "  █   ",
        "  █   "
    ],
    
    # Water - wavy pattern
    "water": [
        "∼∼∼∼∼∼",
        "~~~~~~",
        "∼∼∼∼∼∼",
        "~~~~~~",
        "∼∼∼∼∼∼",
        "~~~~~~"
    ],
    
    # Key - classic key shape
    "key": [
        " ████ ",
        "██  ██",
        "██  ██",
        " ████ ",
        "  ██  ",
        " ████ "
    ],
    
    # Door - door with handle
    "door": [
        "██████",
        "█    █",
        "█  ● █",
        "█    █",
        "█    █",
        "██████"
    ],
    
    # Heart - for win objects
    "heart": [
        " ██ ██",
        "██████",
        "██████",
        " ████ ",
        "  ██  ",
        "      "
    ],
    
    # Star - alternative win object
    "star": [
        "  ██  ",
        " ████ ",
        "██████",
        " ████ ",
        "██  ██",
        "      "
    ],
    
    # Skull - for defeat objects
    "skull": [
        " ████ ",
        "██████",
        "██  ██",
        "██████",
        " ████ ",
        "▼▼▼▼▼▼"
    ],
    
    # Box - pushable container
    "box": [
        "██████",
        "█┌──┐█",
        "█│  │█",
        "█│  │█",
        "█└──┘█",
        "██████"
    ],
    
    # Lava - dangerous terrain
    "lava": [
        "▓▓░░▓▓",
        "░▓▓▓░░",
        "▓░░▓▓▓",
        "▓▓▓░░▓",
        "░░▓▓▓░",
        "▓░░▓▓▓"
    ],
    
    # Tree - static obstacle
    "tree": [
        " ████ ",
        "██████",
        "██████",
        " ████ ",
        "  ██  ",
        "  ██  "
    ],
    
    # Grass - decoration
    "grass": [
        "  ▲ ▲ ",
        " ▲▲▲▲ ",
        "▲▲▲▲▲▲",
        " ││││ ",
        " ││││ ",
        "      "
    ]
}

# Text patterns - smaller, cleaner
TEXT_PATTERNS = {
    "BABA": [
        "████ ",
        "█  █ ",
        "████ ",
        "█  █ ",
        "████ "
    ],
    
    "IS": [
        "███  ",
        " █   ",
        " █   ",
        " █   ",
        "███  "
    ],
    
    "YOU": [
        "█ █  ",
        "█ █  ",
        "███  ",
        " █   ",
        " █   "
    ],
    
    "WIN": [
        "█ █ █",
        "█ █ █",
        "█ █ █",
        "█████",
        "█ █ █"
    ],
    
    "STOP": [
        "████ ",
        "█    ",
        "███  ",
        "   █ ",
        "████ "
    ],
    
    "PUSH": [
        "███  ",
        "█ █  ",
        "███  ",
        "█    ",
        "█    "
    ],
    
    "WALL": [
        "█ █ █",
        "█ █ █",
        "█████",
        "█ █ █",
        "█ █ █"
    ],
    
    "ROCK": [
        "███  ",
        "█ █  ",
        "██   ",
        "█ █  ",
        "█ █  "
    ],
    
    "FLAG": [
        "████ ",
        "█    ",
        "███  ",
        "█    ",
        "█    "
    ],
    
    "WATER": [
        "█ █ █",
        "█ █ █",
        "█████",
        "█ █ █",
        "█ █ █"
    ],
    
    "SINK": [
        "████ ",
        "█    ",
        "███  ",
        " █   ",
        "███  "
    ],
    
    "FLOAT": [
        "████ ",
        "█    ",
        "███  ",
        "█    ",
        "█    "
    ],
    
    "HOT": [
        "█ █  ",
        "█ █  ",
        "███  ",
        "█ █  ",
        "█ █  "
    ],
    
    "MELT": [
        "█   █",
        "██ ██",
        "█ █ █",
        "█   █",
        "█   █"
    ]
}


def create_object_sprite(
    obj_name: str, 
    color: Tuple[int, int, int],
    size: Tuple[int, int] = (24, 24)
) -> np.ndarray:
    """
    Create a sprite for a game object.
    
    Args:
        obj_name: Name of the object
        color: Object color
        size: Sprite size
    
    Returns:
        Sprite as numpy array
    """
    pattern = SPRITE_PATTERNS.get(obj_name)
    
    if pattern:
        # Add some shading for depth
        sprite = create_sprite_from_pattern(pattern, color, (0, 0, 0), size)
        
        # Add highlight and shadow for 3D effect
        sprite = add_3d_effect(sprite, color)
        
        return sprite
    else:
        # Fallback to a simple colored square with symbol
        sprite = np.zeros((*size, 3), dtype=np.uint8)
        # Draw a rounded rectangle
        cv2.rectangle(sprite, (2, 2), (size[0]-3, size[1]-3), color, -1)
        
        # Add first letter of object name
        if obj_name:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(sprite, obj_name[0].upper(), (7, 17), font, 0.5, (255, 255, 255), 1)
        
        return sprite


def create_text_sprite(
    text: str,
    color: Tuple[int, int, int],
    size: Tuple[int, int] = (24, 24)
) -> np.ndarray:
    """
    Create a sprite for text objects.
    
    Args:
        text: Text to display
        color: Text color
        size: Sprite size
    
    Returns:
        Sprite with text
    """
    # Black background
    sprite = np.zeros((*size, 3), dtype=np.uint8)
    
    # Check if we have a pattern for this text
    pattern = TEXT_PATTERNS.get(text)
    
    if pattern:
        # Create from pattern
        text_sprite = create_sprite_from_pattern(pattern, color, (0, 0, 0), (size[0]-4, size[1]-4))
        # Center it
        sprite[2:-2, 2:-2] = text_sprite
    else:
        # Fallback to CV2 text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.3
        thickness = 1
        
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(text[:4], font, font_scale, thickness)
        
        # Center the text
        x = (size[0] - text_width) // 2
        y = (size[1] + text_height) // 2
        
        # Draw the text
        cv2.putText(sprite, text[:4], (x, y), font, font_scale, color, thickness)
    
    # Add border for text objects
    cv2.rectangle(sprite, (1, 1), (size[0]-2, size[1]-2), color, 1)
    
    return sprite


def add_3d_effect(
    sprite: np.ndarray,
    base_color: Tuple[int, int, int]
) -> np.ndarray:
    """
    Add 3D shading effect to a sprite.
    
    Args:
        sprite: Input sprite
        base_color: Base color for calculating highlights/shadows
    
    Returns:
        Sprite with 3D effect
    """
    result = sprite.copy()
    h, w = sprite.shape[:2]
    
    # Create highlight color (lighter)
    highlight = tuple(min(255, int(c * 1.3)) for c in base_color)
    
    # Create shadow color (darker)
    shadow = tuple(int(c * 0.7) for c in base_color)
    
    # Add highlights on top-left edges
    for y in range(h):
        for x in range(w):
            if np.array_equal(sprite[y, x], base_color):
                # Top edge
                if y > 0 and not np.array_equal(sprite[y-1, x], base_color):
                    result[y, x] = highlight
                # Left edge
                elif x > 0 and not np.array_equal(sprite[y, x-1], base_color):
                    result[y, x] = highlight
                # Bottom edge
                elif y < h-1 and not np.array_equal(sprite[y+1, x], base_color):
                    result[y, x] = shadow
                # Right edge
                elif x < w-1 and not np.array_equal(sprite[y, x+1], base_color):
                    result[y, x] = shadow
    
    return result


def create_animated_sprite(
    obj_name: str,
    color: Tuple[int, int, int],
    frame: int = 0,
    size: Tuple[int, int] = (24, 24)
) -> np.ndarray:
    """
    Create an animated sprite (for objects like water).
    
    Args:
        obj_name: Name of the object
        color: Object color
        frame: Animation frame number
        size: Sprite size
    
    Returns:
        Animated sprite frame
    """
    if obj_name == "water":
        # Create animated water pattern
        patterns = [
            [
                "∼∼∼∼∼∼",
                "~~~~~~",
                "∼∼∼∼∼∼",
                "~~~~~~",
                "∼∼∼∼∼∼",
                "~~~~~~"
            ],
            [
                "~~~~~~",
                "∼∼∼∼∼∼",
                "~~~~~~",
                "∼∼∼∼∼∼",
                "~~~~~~",
                "∼∼∼∼∼∼"
            ]
        ]
        pattern = patterns[frame % 2]
        return create_sprite_from_pattern(pattern, color, (0, 0, 0), size)
    else:
        # No animation for other objects
        return create_object_sprite(obj_name, color, size)