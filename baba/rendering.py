"""Rendering utilities for Baba Is You."""

import os
from pathlib import Path
from typing import Optional, Tuple, Union

import cv2
import numpy as np


# Cache for loaded sprites
_sprite_cache = {}


def get_asset_path() -> Path:
    """Get the path to the assets directory."""
    # Try to find assets in various locations
    possible_paths = [
        Path(__file__).parent / "assets",
        Path(__file__).parent.parent / "assets",
        Path.cwd() / "assets",
        Path.cwd() / "baba_is_you" / "assets",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # If no assets found, create a placeholder directory
    default_path = Path(__file__).parent / "assets"
    default_path.mkdir(exist_ok=True)
    return default_path


def load_icon(icon_name: str) -> np.ndarray:
    """
    Load an icon sprite from the assets directory.

    Args:
        icon_name: Name of the icon file (without extension)

    Returns:
        Icon as numpy array, or a placeholder if not found
    """
    if icon_name in _sprite_cache:
        return _sprite_cache[icon_name].copy()
    
    asset_path = get_asset_path()
    
    # Try different extensions
    for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        icon_path = asset_path / f"{icon_name}{ext}"
        if icon_path.exists():
            sprite = cv2.imread(str(icon_path))
            if sprite is not None:
                # Convert BGR to RGB
                sprite = cv2.cvtColor(sprite, cv2.COLOR_BGR2RGB)
                _sprite_cache[icon_name] = sprite
                return sprite.copy()
    
    # Return a placeholder sprite if not found
    placeholder = create_placeholder_sprite()
    _sprite_cache[icon_name] = placeholder
    return placeholder.copy()


def create_placeholder_sprite(size: Tuple[int, int] = (24, 24)) -> np.ndarray:
    """
    Create a placeholder sprite.

    Args:
        size: Size of the sprite (width, height)

    Returns:
        Placeholder sprite as numpy array
    """
    sprite = np.full((*size, 3), 128, dtype=np.uint8)  # Gray background
    # Add a simple pattern to indicate it's a placeholder
    sprite[::4, ::4] = [200, 200, 200]
    return sprite


def tiny_sprite(
    text: str, 
    color: Tuple[int, int, int], 
    size: Tuple[int, int] = (24, 24)
) -> np.ndarray:
    """
    Create a tiny sprite with text.

    Args:
        text: Text to display
        color: RGB color tuple
        size: Size of the sprite

    Returns:
        Sprite as numpy array
    """
    # Import our new sprite functions
    from .sprites import create_text_sprite, create_object_sprite
    
    # Check if this is a text object (all caps)
    if text.isupper():
        return create_text_sprite(text, color, size)
    else:
        # Try to create an object sprite
        return create_object_sprite(text.lower(), color, size)


def add_border(
    sprite: np.ndarray, 
    color: Tuple[int, int, int] = (255, 255, 255), 
    thickness: int = 1
) -> np.ndarray:
    """
    Add a border to a sprite.

    Args:
        sprite: Input sprite
        color: Border color
        thickness: Border thickness

    Returns:
        Sprite with border
    """
    bordered = sprite.copy()
    h, w = sprite.shape[:2]
    
    # Draw rectangle border
    cv2.rectangle(bordered, (0, 0), (w-1, h-1), color, thickness)
    
    return bordered


def get_icon_for_object(obj_name: str, is_text: bool = False) -> np.ndarray:
    """
    Get the icon for a specific object.

    Args:
        obj_name: Name of the object
        is_text: Whether this is a text object

    Returns:
        Icon sprite
    """
    if is_text:
        icon_name = f"text_{obj_name}_0_1"
    else:
        icon_name = f"object_{obj_name}_4"
    
    return load_icon(icon_name)


def composite_sprites(
    sprites: list[np.ndarray], 
    positions: list[Tuple[int, int]], 
    canvas_size: Tuple[int, int]
) -> np.ndarray:
    """
    Composite multiple sprites onto a canvas.

    Args:
        sprites: List of sprites to composite
        positions: List of (x, y) positions for each sprite
        canvas_size: Size of the output canvas (width, height)

    Returns:
        Composited image
    """
    canvas = np.zeros((*canvas_size[::-1], 3), dtype=np.uint8)
    
    for sprite, (x, y) in zip(sprites, positions):
        h, w = sprite.shape[:2]
        
        # Calculate the region to paste (handling boundaries)
        y1 = max(0, y)
        y2 = min(canvas_size[1], y + h)
        x1 = max(0, x)
        x2 = min(canvas_size[0], x + w)
        
        # Calculate the corresponding region in the sprite
        sy1 = max(0, -y)
        sy2 = sy1 + (y2 - y1)
        sx1 = max(0, -x)
        sx2 = sx1 + (x2 - x1)
        
        # Paste the sprite
        if y2 > y1 and x2 > x1:
            canvas[y1:y2, x1:x2] = sprite[sy1:sy2, sx1:sx2]
    
    return canvas


def scale_sprite(sprite: np.ndarray, scale: float) -> np.ndarray:
    """
    Scale a sprite by a given factor.

    Args:
        sprite: Input sprite
        scale: Scale factor

    Returns:
        Scaled sprite
    """
    h, w = sprite.shape[:2]
    new_size = (int(w * scale), int(h * scale))
    
    if scale > 1:
        interpolation = cv2.INTER_LINEAR
    else:
        interpolation = cv2.INTER_AREA
    
    return cv2.resize(sprite, new_size, interpolation=interpolation)


def create_grid_lines(
    size: Tuple[int, int], 
    cell_size: int, 
    color: Tuple[int, int, int] = (50, 50, 50),
    thickness: int = 1
) -> np.ndarray:
    """
    Create grid lines overlay.

    Args:
        size: Size of the grid (width, height) in pixels
        cell_size: Size of each cell
        color: Color of the grid lines
        thickness: Thickness of the lines

    Returns:
        Grid overlay with transparent background
    """
    # Create RGBA image for transparency
    overlay = np.zeros((*size[::-1], 4), dtype=np.uint8)
    
    # Draw vertical lines
    for x in range(0, size[0] + 1, cell_size):
        cv2.line(overlay, (x, 0), (x, size[1]), (*color, 255), thickness)
    
    # Draw horizontal lines
    for y in range(0, size[1] + 1, cell_size):
        cv2.line(overlay, (0, y), (size[0], y), (*color, 255), thickness)
    
    return overlay