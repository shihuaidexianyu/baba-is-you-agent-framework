"""
Baba Is You game entities.

This module defines all game objects including:
- Regular objects (Baba, Rock, Wall, Flag, etc.)
- Text objects (BABA, IS, YOU, etc.)
- Base classes for extensibility

Objects in Baba Is You have two forms:
1. Regular objects: The actual game entities that move and interact
2. Text objects: Words that form rules when arranged properly
"""

import os
from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, List, Optional, Tuple, Union

import cv2
import numpy as np

from .rendering import add_border, load_icon, tiny_sprite
from .properties import Property


@dataclass(eq=False)
class Object:
    """
    Base class for all game objects (both regular objects and text).
    
    Key attributes:
    - name: Object identifier (e.g., "baba", "rock", "baba_text")
    - type_id: Unique numeric ID for fast comparison
    - color: RGB color for rendering
    - is_text: Whether this is a text object that can form rules
    - properties: List of inherent properties (rarely used, most properties come from rules)
    
    Objects are hashable and comparable by their type_id.
    """

    name: str = ""
    type_id: int = 0
    color: Optional[Union[Tuple[int, int, int], np.ndarray]] = None
    sprite: Optional[np.ndarray] = None
    is_text: bool = False
    traversible: bool = True
    displaceable: Optional[bool] = None
    properties: List["Property"] = field(default_factory=list)

    @property
    def noun(self):
        """For text objects, returns the noun they represent."""
        return self.name if self.is_text else None

    @property
    def referenced_type(self):
        """For regular objects, returns their type name."""
        return self.name if not self.is_text else None

    def __hash__(self):
        return hash(self.type_id)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Object):
            return self.type_id == other.type_id
        else:
            return NotImplemented

    def __repr__(self):
        return f"Object[{self.name}/{self.type_id}, text:{self.is_text}]"

    def render(self, size=(24, 24), variant: int = 0):
        """
        Render the object as a sprite image.
        
        First attempts to use official game sprites if available,
        then falls back to custom ASCII-based sprites.
        
        Args:
            size: Desired sprite size in pixels
            variant: Sprite variant (for animation, not fully implemented)
            
        Returns:
            Numpy array representing the sprite image
        """
        # Try to load actual game sprite first (if available)
        from .sprite_loader import sprite_loader
        
        if sprite_loader.has_real_sprites:
            # Determine sprite name
            if self.is_text:
                sprite_name = self.name  # Already includes _text suffix
            else:
                sprite_name = self.name
                
            sprite = sprite_loader.load_sprite(sprite_name, size)
            
            if sprite is not None:
                return sprite
        
        # Fallback to our custom generated sprites
        # Remove _text suffix for text objects when generating sprite
        text = self.name[:-5] if self.is_text else self.name
        sprite = tiny_sprite(text.upper() if self.is_text else text, self.color or (100, 100, 100))
        # rescale sprite to requested size
        sprite = cv2.resize(sprite, size, interpolation=cv2.INTER_NEAREST)
        sprite = sprite.astype(np.uint8)
        return sprite


@dataclass(eq=False)
class BabaObject(Object):
    """The main character - Baba! Usually controlled by the player."""
    name: str = "baba"
    sprite: np.ndarray = field(default_factory=lambda: load_icon("object_00_4"))
    color: Tuple[int, int, int] = (255, 255, 255)  # White
    is_text: bool = False
    displaceable: bool = True


@dataclass(eq=False)
class WallObject(Object):
    name: str = "wall"
    sprite: np.ndarray = field(default_factory=lambda: load_icon("object_01_4"))
    color: Tuple[int, int, int] = (139, 69, 19)  # Saddle brown
    traversible: bool = False
    displaceable: bool = False


@dataclass(eq=False)
class RockObject(Object):
    name: str = "rock"
    sprite: np.ndarray = field(default_factory=lambda: load_icon("object_04_4"))
    color: Tuple[int, int, int] = (169, 169, 169)  # Dark gray
    displaceable: bool = True


@dataclass(eq=False)
class FlagObject(Object):
    name: str = "flag"
    sprite: np.ndarray = field(default_factory=lambda: load_icon("object_06_4"))
    color: Tuple[int, int, int] = (255, 215, 0)  # Gold
    displaceable: bool = True


@dataclass(eq=False)
class WaterObject(Object):
    name: str = "water"
    sprite: np.ndarray = field(default_factory=lambda: load_icon("object_13_4"))
    color: Tuple[int, int, int] = (64, 164, 223)  # Nice blue
    is_traversible: bool = False
    displaceable: bool = False


@dataclass(eq=False)
class TextObject(Object):
    """
    Base class for all text objects.
    
    Text objects are always pushable and form rules when arranged properly.
    They have special attributes:
    - noun: For noun text (BABA, ROCK, etc.)
    - verb: For verb text (IS, HAS, etc.)
    - property: For property text (YOU, WIN, PUSH, etc.)
    """
    is_text: bool = True
    displaceable: bool = True  # Text is always pushable
    noun: Optional[str] = None


def _capitalize(text):
    if text:
        return text[0].upper() + text[1:]
    else:
        return text


@dataclass(eq=False)
class BabaTextObject(TextObject):
    """Text object 'BABA' - used in rules like 'BABA IS YOU'."""
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_00_4"))
    color: Tuple[int, int, int] = (255, 182, 193)  # Light pink
    text: str = "BABA"  # Display text
    noun: str = "baba"  # The object type this text refers to

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class IsTextObject(TextObject):
    """The verb 'IS' - connects nouns to properties or other nouns."""
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_is_0_1"))
    color: Tuple[int, int, int] = (255, 255, 255)  # White
    text: str = "IS"
    verb: str = "is"  # Added verb attribute for rule parsing
    is_operator: bool = True

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class YouTextObject(TextObject):
    """Property text 'YOU' - makes objects player-controlled."""
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_you_0_1"))
    color: Tuple[int, int, int] = (255, 192, 203)  # Pink
    text: str = "YOU"
    is_property: bool = True
    property: Property = Property.YOU  # Links to the Property enum

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class WallTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_01_4"))
    color: Tuple[int, int, int] = (210, 180, 140)  # Tan
    text: str = "WALL"
    noun: str = "wall"

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class StopTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_push_0_1"))
    color: Tuple[int, int, int] = (220, 20, 60)  # Crimson
    text: str = "STOP"
    is_property: bool = True
    property: Property = Property.STOP

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class PushTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_push_0_1"))
    color: Tuple[int, int, int] = (144, 238, 144)  # Light green
    text: str = "PUSH"
    is_property: bool = True
    property: Property = Property.PUSH

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class RockTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_04_4"))
    color: Tuple[int, int, int] = (192, 192, 192)  # Silver
    text: str = "ROCK"
    noun: str = "rock"

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class FlagTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_06_4"))
    color: Tuple[int, int, int] = (255, 255, 102)  # Light yellow
    text: str = "FLAG"
    noun: str = "flag"

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class WinTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_win_0_1"))
    color: Tuple[int, int, int] = (255, 215, 0)  # Gold
    text: str = "WIN"
    is_property: bool = True
    property: Property = Property.WIN

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class SinkTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_sink_0_1"))
    color: Tuple[int, int, int] = (138, 43, 226)  # Blue violet
    text: str = "SINK"
    is_property: bool = True
    property: Property = Property.SINK

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


@dataclass(eq=False)
class WaterTextObject(TextObject):
    sprite: np.ndarray = field(default_factory=lambda: load_icon("text_13_4"))
    color: Tuple[int, int, int] = (135, 206, 235)  # Sky blue
    text: str = "WATER"
    noun: str = "water"

    def render(self, size=(24, 24), variant: int = 0):
        sprite = super().render(size, variant)
        sprite = add_border(sprite, thickness=2)
        return sprite


class Palette:
    """
    Color palette for object rendering.
    
    Provides a consistent set of colors for the custom sprite system.
    Colors are used when official sprites are not available.

    Source: https://www.colourlovers.com/palette/146729/severed_garden
    """

    gray = (65, 62, 74)
    dark_gray = (37, 36, 34)
    black = (10, 10, 10)
    white = (229, 221, 197)
    red = (152, 79, 79)
    orange = (255, 147, 79)
    yellow = (255, 243, 79)
    olive = (171, 199, 85)
    green = (140, 217, 140)
    teal = (124, 188, 196)
    cyan = (79, 243, 255)
    blue = (99, 121, 188)
    purple = (219, 123, 196)
    pink = (243, 182, 213)
    brown = (129, 104, 86)