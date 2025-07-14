"""
Game properties for Baba Is You.

Properties are attributes that can be assigned to objects through rules.
For example, "BABA IS YOU" gives the YOU property to all BABA objects.

Each property has specific game mechanics associated with it.
"""

from enum import Enum


class Property(Enum):
    """
    Game object properties that can be assigned by rules.

    Properties define object behavior and are assigned through rules like:
    - BABA IS YOU (gives control to the player)
    - FLAG IS WIN (makes touching it win the level)
    - WALL IS STOP (makes it block movement)

    Core properties and their effects:
    """

    # Movement and control
    YOU = "YOU"  # Makes object player-controlled
    MOVE = "MOVE"  # Makes object move automatically
    SHIFT = "SHIFT"  # Special movement behavior

    # Interaction properties
    STOP = "STOP"  # Blocks movement of other objects
    PUSH = "PUSH"  # Can be pushed by YOU objects
    PULL = "PULL"  # Pulls objects when moved
    SWAP = "SWAP"  # Swaps positions with other objects

    # Win/lose conditions
    WIN = "WIN"  # Touching this with YOU wins the level
    DEFEAT = "DEFEAT"  # Touching this with YOU loses the level
    END = "END"  # Special end condition

    # Destruction properties
    SINK = "SINK"  # Destroys everything at same position
    HOT = "HOT"  # Melts MELT objects
    MELT = "MELT"  # Destroyed by HOT objects
    WEAK = "WEAK"  # Destroyed by any overlapping object

    # State changes
    OPEN = "OPEN"  # Can be opened (with SHUT objects)
    SHUT = "SHUT"  # Closed state (pairs with OPEN)

    # Special mechanics
    FLOAT = "FLOAT"  # Can exist on top of other objects
    TELE = "TELE"  # Teleportation behavior
