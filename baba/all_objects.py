"""Complete set of all Baba Is You objects."""

from dataclasses import dataclass

from .properties import Property
from .world_object import Object, TextObject

# =============================================================================
# BASE CLASSES
# =============================================================================


@dataclass(eq=False)
class GameObject(Object):
    """Base class for regular game objects."""

    char: str = "?"
    is_text: bool = False
    displaceable: bool = True
    traversible: bool = True


@dataclass(eq=False)
class TextGameObject(TextObject):
    """Base class for text objects."""

    is_text: bool = True
    color: tuple[int, int, int] = (200, 200, 200)  # Default text color

    @property
    def text(self):
        """Get the text to display."""
        if hasattr(self, "noun") and self.noun:
            return self.noun.upper()
        elif hasattr(self, "verb") and self.verb:
            return self.verb.upper()
        elif hasattr(self, "property") and self.property:
            return self.property.name
        elif hasattr(self, "special") and self.special:
            return self.special.upper()
        else:
            # Fallback to extracting from name
            if self.name.startswith("text_"):
                return self.name[5:].upper()
            return self.name.upper()


# =============================================================================
# CHARACTERS (IDs 1-4)
# =============================================================================


@dataclass(eq=False)
class BabaObject(GameObject):
    name: str = "baba"
    type_id: int = 1
    color: tuple[int, int, int] = (255, 255, 255)  # White
    char: str = "B"


@dataclass(eq=False)
class KekeObject(GameObject):
    name: str = "keke"
    type_id: int = 2
    color: tuple[int, int, int] = (255, 100, 100)  # Red/Pink
    char: str = "K"


@dataclass(eq=False)
class AnniObject(GameObject):
    name: str = "anni"
    type_id: int = 3
    color: tuple[int, int, int] = (200, 100, 200)  # Purple
    char: str = "A"


@dataclass(eq=False)
class MeObject(GameObject):
    name: str = "me"
    type_id: int = 4
    color: tuple[int, int, int] = (100, 100, 255)  # Blue
    char: str = "M"


# =============================================================================
# STRUCTURES (IDs 5-11)
# =============================================================================


@dataclass(eq=False)
class WallObject(GameObject):
    name: str = "wall"
    type_id: int = 5
    color: tuple[int, int, int] = (139, 69, 19)  # Brown
    char: str = "W"
    traversible: bool = False
    displaceable: bool = False


@dataclass(eq=False)
class RockObject(GameObject):
    name: str = "rock"
    type_id: int = 6
    color: tuple[int, int, int] = (169, 169, 169)  # Gray
    char: str = "O"


@dataclass(eq=False)
class FlagObject(GameObject):
    name: str = "flag"
    type_id: int = 7
    color: tuple[int, int, int] = (255, 215, 0)  # Gold
    char: str = "F"


@dataclass(eq=False)
class TileObject(GameObject):
    name: str = "tile"
    type_id: int = 8
    color: tuple[int, int, int] = (200, 200, 150)  # Light tan
    char: str = "="


@dataclass(eq=False)
class GrassObject(GameObject):
    name: str = "grass"
    type_id: int = 9
    color: tuple[int, int, int] = (50, 200, 50)  # Green
    char: str = ","


@dataclass(eq=False)
class BrickObject(GameObject):
    name: str = "brick"
    type_id: int = 10
    color: tuple[int, int, int] = (165, 42, 42)  # Brick red
    char: str = "#"


@dataclass(eq=False)
class HedgeObject(GameObject):
    name: str = "hedge"
    type_id: int = 11
    color: tuple[int, int, int] = (0, 100, 0)  # Dark green
    char: str = "H"


# =============================================================================
# LIQUIDS (IDs 12-14)
# =============================================================================


@dataclass(eq=False)
class WaterObject(GameObject):
    name: str = "water"
    type_id: int = 12
    color: tuple[int, int, int] = (30, 144, 255)  # Dodger blue
    char: str = "~"


@dataclass(eq=False)
class LavaObject(GameObject):
    name: str = "lava"
    type_id: int = 13
    color: tuple[int, int, int] = (255, 69, 0)  # Orange red
    char: str = "L"


@dataclass(eq=False)
class BogObject(GameObject):
    name: str = "bog"
    type_id: int = 14
    color: tuple[int, int, int] = (107, 142, 35)  # Olive drab
    char: str = "&"


# =============================================================================
# INTERACTIVE OBJECTS (IDs 15-22)
# =============================================================================


@dataclass(eq=False)
class DoorObject(GameObject):
    name: str = "door"
    type_id: int = 15
    color: tuple[int, int, int] = (139, 90, 43)  # Tan
    char: str = "D"


@dataclass(eq=False)
class KeyObject(GameObject):
    name: str = "key"
    type_id: int = 16
    color: tuple[int, int, int] = (255, 223, 0)  # Golden
    char: str = "k"


@dataclass(eq=False)
class SkullObject(GameObject):
    name: str = "skull"
    type_id: int = 17
    color: tuple[int, int, int] = (245, 245, 245)  # White smoke
    char: str = "S"


@dataclass(eq=False)
class FungusObject(GameObject):
    name: str = "fungus"
    type_id: int = 18
    color: tuple[int, int, int] = (139, 0, 139)  # Dark magenta
    char: str = "U"


@dataclass(eq=False)
class FlowerObject(GameObject):
    name: str = "flower"
    type_id: int = 19
    color: tuple[int, int, int] = (255, 192, 203)  # Pink
    char: str = "*"


@dataclass(eq=False)
class BoltObject(GameObject):
    name: str = "bolt"
    type_id: int = 20
    color: tuple[int, int, int] = (255, 255, 0)  # Yellow
    char: str = "!"


@dataclass(eq=False)
class PillarObject(GameObject):
    name: str = "pillar"
    type_id: int = 21
    color: tuple[int, int, int] = (160, 160, 160)  # Gray
    char: str = "I"


@dataclass(eq=False)
class BoxObject(GameObject):
    name: str = "box"
    type_id: int = 22
    color: tuple[int, int, int] = (184, 134, 11)  # Dark goldenrod
    char: str = "□"


# =============================================================================
# MECHANICAL (IDs 23)
# =============================================================================


@dataclass(eq=False)
class BeltObject(GameObject):
    name: str = "belt"
    type_id: int = 23
    color: tuple[int, int, int] = (70, 70, 70)  # Dark gray
    char: str = ">"


# =============================================================================
# CREATURES (IDs 24-27, 40-43)
# =============================================================================


@dataclass(eq=False)
class BugObject(GameObject):
    name: str = "bug"
    type_id: int = 24
    color: tuple[int, int, int] = (0, 255, 0)  # Lime
    char: str = "b"


@dataclass(eq=False)
class FoliageObject(GameObject):
    name: str = "foliage"
    type_id: int = 25
    color: tuple[int, int, int] = (34, 139, 34)  # Forest green
    char: str = "f"


@dataclass(eq=False)
class AlgaeObject(GameObject):
    name: str = "algae"
    type_id: int = 26
    color: tuple[int, int, int] = (0, 128, 128)  # Teal
    char: str = "a"


@dataclass(eq=False)
class JellyObject(GameObject):
    name: str = "jelly"
    type_id: int = 27
    color: tuple[int, int, int] = (138, 43, 226)  # Blue violet
    char: str = "J"


@dataclass(eq=False)
class BatObject(GameObject):
    name: str = "bat"
    type_id: int = 40
    color: tuple[int, int, int] = (75, 0, 130)  # Indigo
    char: str = "V"


@dataclass(eq=False)
class BubbleObject(GameObject):
    name: str = "bubble"
    type_id: int = 41
    color: tuple[int, int, int] = (173, 216, 230)  # Light blue
    char: str = "o"


@dataclass(eq=False)
class BirdObject(GameObject):
    name: str = "bird"
    type_id: int = 42
    color: tuple[int, int, int] = (135, 206, 235)  # Sky blue
    char: str = "v"


@dataclass(eq=False)
class HandObject(GameObject):
    name: str = "hand"
    type_id: int = 43
    color: tuple[int, int, int] = (255, 228, 196)  # Bisque
    char: str = "h"


# =============================================================================
# NATURE (IDs 28-34, 37-39)
# =============================================================================


@dataclass(eq=False)
class TreeObject(GameObject):
    name: str = "tree"
    type_id: int = 28
    color: tuple[int, int, int] = (0, 128, 0)  # Green
    char: str = "T"


@dataclass(eq=False)
class FruitObject(GameObject):
    name: str = "fruit"
    type_id: int = 29
    color: tuple[int, int, int] = (255, 0, 0)  # Red
    char: str = "Q"


@dataclass(eq=False)
class RoseObject(GameObject):
    name: str = "rose"
    type_id: int = 30
    color: tuple[int, int, int] = (255, 0, 127)  # Rose
    char: str = "@"


@dataclass(eq=False)
class LoveObject(GameObject):
    name: str = "love"
    type_id: int = 31
    color: tuple[int, int, int] = (255, 105, 180)  # Hot pink
    char: str = "♥"


@dataclass(eq=False)
class MoonObject(GameObject):
    name: str = "moon"
    type_id: int = 32
    color: tuple[int, int, int] = (245, 245, 220)  # Beige
    char: str = "C"


@dataclass(eq=False)
class StarObject(GameObject):
    name: str = "star"
    type_id: int = 33
    color: tuple[int, int, int] = (255, 255, 0)  # Yellow
    char: str = "★"


@dataclass(eq=False)
class DustObject(GameObject):
    name: str = "dust"
    type_id: int = 34
    color: tuple[int, int, int] = (210, 180, 140)  # Tan
    char: str = "."


@dataclass(eq=False)
class IceObject(GameObject):
    name: str = "ice"
    type_id: int = 37
    color: tuple[int, int, int] = (175, 238, 238)  # Pale turquoise
    char: str = "i"


@dataclass(eq=False)
class LeafObject(GameObject):
    name: str = "leaf"
    type_id: int = 38
    color: tuple[int, int, int] = (154, 205, 50)  # Yellow green
    char: str = "l"


@dataclass(eq=False)
class HuskObject(GameObject):
    name: str = "husk"
    type_id: int = 39
    color: tuple[int, int, int] = (160, 82, 45)  # Sienna
    char: str = "u"


# =============================================================================
# MECHANICAL/SPECIAL (IDs 35-36, 44)
# =============================================================================


@dataclass(eq=False)
class RobotObject(GameObject):
    name: str = "robot"
    type_id: int = 35
    color: tuple[int, int, int] = (192, 192, 192)  # Silver
    char: str = "R"


@dataclass(eq=False)
class CogObject(GameObject):
    name: str = "cog"
    type_id: int = 36
    color: tuple[int, int, int] = (128, 128, 128)  # Gray
    char: str = "⚙"


@dataclass(eq=False)
class CupObject(GameObject):
    name: str = "cup"
    type_id: int = 44
    color: tuple[int, int, int] = (255, 248, 220)  # Cornsilk
    char: str = "U"


# =============================================================================
# TEXT OBJECTS - NOUNS (IDs 46-89)
# =============================================================================


@dataclass(eq=False)
class BabaTextObject(TextGameObject):
    name: str = "text_baba"
    type_id: int = 46
    noun: str = "baba"
    color: tuple[int, int, int] = (255, 200, 200)


@dataclass(eq=False)
class KekeTextObject(TextGameObject):
    name: str = "text_keke"
    type_id: int = 47
    noun: str = "keke"
    color: tuple[int, int, int] = (255, 150, 150)


@dataclass(eq=False)
class AnniTextObject(TextGameObject):
    name: str = "text_anni"
    type_id: int = 48
    noun: str = "anni"
    color: tuple[int, int, int] = (255, 150, 255)


@dataclass(eq=False)
class MeTextObject(TextGameObject):
    name: str = "text_me"
    type_id: int = 49
    noun: str = "me"
    color: tuple[int, int, int] = (150, 150, 255)


@dataclass(eq=False)
class WallTextObject(TextGameObject):
    name: str = "text_wall"
    type_id: int = 50
    noun: str = "wall"
    color: tuple[int, int, int] = (200, 150, 100)


@dataclass(eq=False)
class RockTextObject(TextGameObject):
    name: str = "text_rock"
    type_id: int = 51
    noun: str = "rock"
    color: tuple[int, int, int] = (200, 200, 200)


@dataclass(eq=False)
class FlagTextObject(TextGameObject):
    name: str = "text_flag"
    type_id: int = 52
    noun: str = "flag"
    color: tuple[int, int, int] = (255, 255, 150)


@dataclass(eq=False)
class TileTextObject(TextGameObject):
    name: str = "text_tile"
    type_id: int = 53
    noun: str = "tile"
    color: tuple[int, int, int] = (220, 220, 180)


@dataclass(eq=False)
class GrassTextObject(TextGameObject):
    name: str = "text_grass"
    type_id: int = 54
    noun: str = "grass"
    color: tuple[int, int, int] = (150, 255, 150)


@dataclass(eq=False)
class BrickTextObject(TextGameObject):
    name: str = "text_brick"
    type_id: int = 55
    noun: str = "brick"
    color: tuple[int, int, int] = (200, 100, 100)


@dataclass(eq=False)
class HedgeTextObject(TextGameObject):
    name: str = "text_hedge"
    type_id: int = 56
    noun: str = "hedge"
    color: tuple[int, int, int] = (100, 200, 100)


@dataclass(eq=False)
class WaterTextObject(TextGameObject):
    name: str = "text_water"
    type_id: int = 57
    noun: str = "water"
    color: tuple[int, int, int] = (150, 200, 255)


@dataclass(eq=False)
class LavaTextObject(TextGameObject):
    name: str = "text_lava"
    type_id: int = 58
    noun: str = "lava"
    color: tuple[int, int, int] = (255, 150, 100)


@dataclass(eq=False)
class BogTextObject(TextGameObject):
    name: str = "text_bog"
    type_id: int = 59
    noun: str = "bog"
    color: tuple[int, int, int] = (150, 180, 100)


@dataclass(eq=False)
class DoorTextObject(TextGameObject):
    name: str = "text_door"
    type_id: int = 60
    noun: str = "door"
    color: tuple[int, int, int] = (180, 140, 100)


@dataclass(eq=False)
class KeyTextObject(TextGameObject):
    name: str = "text_key"
    type_id: int = 61
    noun: str = "key"
    color: tuple[int, int, int] = (255, 230, 150)


@dataclass(eq=False)
class SkullTextObject(TextGameObject):
    name: str = "text_skull"
    type_id: int = 62
    noun: str = "skull"
    color: tuple[int, int, int] = (240, 240, 240)


@dataclass(eq=False)
class FungusTextObject(TextGameObject):
    name: str = "text_fungus"
    type_id: int = 63
    noun: str = "fungus"
    color: tuple[int, int, int] = (180, 100, 180)


@dataclass(eq=False)
class FlowerTextObject(TextGameObject):
    name: str = "text_flower"
    type_id: int = 64
    noun: str = "flower"
    color: tuple[int, int, int] = (255, 200, 220)


@dataclass(eq=False)
class BoltTextObject(TextGameObject):
    name: str = "text_bolt"
    type_id: int = 65
    noun: str = "bolt"
    color: tuple[int, int, int] = (255, 255, 150)


@dataclass(eq=False)
class PillarTextObject(TextGameObject):
    name: str = "text_pillar"
    type_id: int = 66
    noun: str = "pillar"
    color: tuple[int, int, int] = (180, 180, 180)


@dataclass(eq=False)
class BoxTextObject(TextGameObject):
    name: str = "text_box"
    type_id: int = 67
    noun: str = "box"
    color: tuple[int, int, int] = (200, 170, 130)


@dataclass(eq=False)
class BeltTextObject(TextGameObject):
    name: str = "text_belt"
    type_id: int = 68
    noun: str = "belt"
    color: tuple[int, int, int] = (120, 120, 120)


@dataclass(eq=False)
class BugTextObject(TextGameObject):
    name: str = "text_bug"
    type_id: int = 69
    noun: str = "bug"
    color: tuple[int, int, int] = (150, 255, 150)


@dataclass(eq=False)
class FoliageTextObject(TextGameObject):
    name: str = "text_foliage"
    type_id: int = 70
    noun: str = "foliage"
    color: tuple[int, int, int] = (100, 180, 100)


@dataclass(eq=False)
class AlgaeTextObject(TextGameObject):
    name: str = "text_algae"
    type_id: int = 71
    noun: str = "algae"
    color: tuple[int, int, int] = (100, 180, 180)


@dataclass(eq=False)
class JellyTextObject(TextGameObject):
    name: str = "text_jelly"
    type_id: int = 72
    noun: str = "jelly"
    color: tuple[int, int, int] = (180, 130, 255)


@dataclass(eq=False)
class TreeTextObject(TextGameObject):
    name: str = "text_tree"
    type_id: int = 73
    noun: str = "tree"
    color: tuple[int, int, int] = (100, 180, 100)


@dataclass(eq=False)
class FruitTextObject(TextGameObject):
    name: str = "text_fruit"
    type_id: int = 74
    noun: str = "fruit"
    color: tuple[int, int, int] = (255, 150, 150)


@dataclass(eq=False)
class RoseTextObject(TextGameObject):
    name: str = "text_rose"
    type_id: int = 75
    noun: str = "rose"
    color: tuple[int, int, int] = (255, 150, 200)


@dataclass(eq=False)
class LoveTextObject(TextGameObject):
    name: str = "text_love"
    type_id: int = 76
    noun: str = "love"
    color: tuple[int, int, int] = (255, 180, 220)


@dataclass(eq=False)
class MoonTextObject(TextGameObject):
    name: str = "text_moon"
    type_id: int = 77
    noun: str = "moon"
    color: tuple[int, int, int] = (240, 240, 200)


@dataclass(eq=False)
class StarTextObject(TextGameObject):
    name: str = "text_star"
    type_id: int = 78
    noun: str = "star"
    color: tuple[int, int, int] = (255, 255, 150)


@dataclass(eq=False)
class DustTextObject(TextGameObject):
    name: str = "text_dust"
    type_id: int = 79
    noun: str = "dust"
    color: tuple[int, int, int] = (200, 180, 160)


@dataclass(eq=False)
class RobotTextObject(TextGameObject):
    name: str = "text_robot"
    type_id: int = 80
    noun: str = "robot"
    color: tuple[int, int, int] = (200, 200, 200)


@dataclass(eq=False)
class CogTextObject(TextGameObject):
    name: str = "text_cog"
    type_id: int = 81
    noun: str = "cog"
    color: tuple[int, int, int] = (160, 160, 160)


@dataclass(eq=False)
class IceTextObject(TextGameObject):
    name: str = "text_ice"
    type_id: int = 82
    noun: str = "ice"
    color: tuple[int, int, int] = (200, 240, 240)


@dataclass(eq=False)
class LeafTextObject(TextGameObject):
    name: str = "text_leaf"
    type_id: int = 83
    noun: str = "leaf"
    color: tuple[int, int, int] = (180, 220, 130)


@dataclass(eq=False)
class HuskTextObject(TextGameObject):
    name: str = "text_husk"
    type_id: int = 84
    noun: str = "husk"
    color: tuple[int, int, int] = (180, 140, 100)


@dataclass(eq=False)
class BatTextObject(TextGameObject):
    name: str = "text_bat"
    type_id: int = 85
    noun: str = "bat"
    color: tuple[int, int, int] = (130, 100, 180)


@dataclass(eq=False)
class BubbleTextObject(TextGameObject):
    name: str = "text_bubble"
    type_id: int = 86
    noun: str = "bubble"
    color: tuple[int, int, int] = (200, 230, 240)


@dataclass(eq=False)
class BirdTextObject(TextGameObject):
    name: str = "text_bird"
    type_id: int = 87
    noun: str = "bird"
    color: tuple[int, int, int] = (180, 220, 240)


@dataclass(eq=False)
class HandTextObject(TextGameObject):
    name: str = "text_hand"
    type_id: int = 88
    noun: str = "hand"
    color: tuple[int, int, int] = (240, 220, 200)


@dataclass(eq=False)
class CupTextObject(TextGameObject):
    name: str = "text_cup"
    type_id: int = 89
    noun: str = "cup"
    color: tuple[int, int, int] = (240, 230, 200)


# =============================================================================
# TEXT OBJECTS - PROPERTIES (IDs 90-105)
# =============================================================================


@dataclass(eq=False)
class YouTextObject(TextGameObject):
    name: str = "text_you"
    type_id: int = 90
    property: Property = Property.YOU
    color: tuple[int, int, int] = (255, 255, 255)


@dataclass(eq=False)
class WinTextObject(TextGameObject):
    name: str = "text_win"
    type_id: int = 91
    property: Property = Property.WIN
    color: tuple[int, int, int] = (255, 215, 0)


@dataclass(eq=False)
class StopTextObject(TextGameObject):
    name: str = "text_stop"
    type_id: int = 92
    property: Property = Property.STOP
    color: tuple[int, int, int] = (200, 100, 100)


@dataclass(eq=False)
class PushTextObject(TextGameObject):
    name: str = "text_push"
    type_id: int = 93
    property: Property = Property.PUSH
    color: tuple[int, int, int] = (200, 150, 100)


@dataclass(eq=False)
class SinkTextObject(TextGameObject):
    name: str = "text_sink"
    type_id: int = 94
    property: Property = Property.SINK
    color: tuple[int, int, int] = (100, 150, 200)


@dataclass(eq=False)
class DefeatTextObject(TextGameObject):
    name: str = "text_defeat"
    type_id: int = 95
    property: Property = Property.DEFEAT
    color: tuple[int, int, int] = (200, 50, 50)


@dataclass(eq=False)
class HotTextObject(TextGameObject):
    name: str = "text_hot"
    type_id: int = 96
    property: Property = Property.HOT
    color: tuple[int, int, int] = (255, 100, 0)


@dataclass(eq=False)
class MeltTextObject(TextGameObject):
    name: str = "text_melt"
    type_id: int = 97
    property: Property = Property.MELT
    color: tuple[int, int, int] = (100, 200, 255)


@dataclass(eq=False)
class MoveTextObject(TextGameObject):
    name: str = "text_move"
    type_id: int = 98
    property: Property = Property.MOVE
    color: tuple[int, int, int] = (150, 255, 150)


@dataclass(eq=False)
class TeleTextObject(TextGameObject):
    name: str = "text_tele"
    type_id: int = 99
    property: Property = Property.TELE
    color: tuple[int, int, int] = (200, 100, 255)


@dataclass(eq=False)
class OpenTextObject(TextGameObject):
    name: str = "text_open"
    type_id: int = 100
    property: Property = Property.OPEN
    color: tuple[int, int, int] = (255, 255, 100)


@dataclass(eq=False)
class ShutTextObject(TextGameObject):
    name: str = "text_shut"
    type_id: int = 101
    property: Property = Property.SHUT
    color: tuple[int, int, int] = (100, 100, 100)


@dataclass(eq=False)
class WeakTextObject(TextGameObject):
    name: str = "text_weak"
    type_id: int = 102
    property: Property = Property.WEAK
    color: tuple[int, int, int] = (150, 150, 150)


@dataclass(eq=False)
class FloatTextObject(TextGameObject):
    name: str = "text_float"
    type_id: int = 103
    property: Property = Property.FLOAT
    color: tuple[int, int, int] = (150, 200, 255)


@dataclass(eq=False)
class PullTextObject(TextGameObject):
    name: str = "text_pull"
    type_id: int = 104
    property: Property = Property.PULL
    color: tuple[int, int, int] = (200, 150, 200)


@dataclass(eq=False)
class ShiftTextObject(TextGameObject):
    name: str = "text_shift"
    type_id: int = 105
    property: Property = Property.SHIFT
    color: tuple[int, int, int] = (255, 200, 100)


# =============================================================================
# TEXT OBJECTS - VERBS (IDs 106-114)
# =============================================================================


@dataclass(eq=False)
class IsTextObject(TextGameObject):
    name: str = "text_is"
    type_id: int = 106
    verb: str = "is"
    color: tuple[int, int, int] = (255, 255, 255)
    noun: str | None = None
    property: Property | None = None
    special: str | None = None


@dataclass(eq=False)
class AndTextObject(TextGameObject):
    name: str = "text_and"
    type_id: int = 107
    verb: str = "and"
    color: tuple[int, int, int] = (255, 255, 255)
    noun: str | None = None
    property: Property | None = None
    special: str | None = None


@dataclass(eq=False)
class NotTextObject(TextGameObject):
    name: str = "text_not"
    type_id: int = 108
    verb: str = "not"
    color: tuple[int, int, int] = (255, 100, 100)
    noun: str | None = None
    property: Property | None = None
    special: str | None = None


# =============================================================================
# SPECIAL TEXT OBJECTS (IDs 115-119)
# =============================================================================


@dataclass(eq=False)
class AllTextObject(TextGameObject):
    name: str = "text_all"
    type_id: int = 115
    special: str = "all"
    color: tuple[int, int, int] = (255, 255, 0)
    noun: str | None = None
    property: Property | None = None
    verb: str | None = None


@dataclass(eq=False)
class TextTextObject(TextGameObject):
    name: str = "text_text"
    type_id: int = 116
    special: str = "text"
    color: tuple[int, int, int] = (200, 200, 255)
    noun: str | None = None
    property: Property | None = None
    verb: str | None = None


@dataclass(eq=False)
class LevelTextObject(TextGameObject):
    name: str = "text_level"
    type_id: int = 119
    special: str = "level"
    color: tuple[int, int, int] = (255, 200, 255)
    noun: str | None = None
    property: Property | None = None
    verb: str | None = None


# =============================================================================
# REGISTRY OF ALL OBJECTS
# =============================================================================

ALL_OBJECTS = {
    # Characters
    "baba": BabaObject,
    "keke": KekeObject,
    "anni": AnniObject,
    "me": MeObject,
    # Structures
    "wall": WallObject,
    "rock": RockObject,
    "flag": FlagObject,
    "tile": TileObject,
    "grass": GrassObject,
    "brick": BrickObject,
    "hedge": HedgeObject,
    # Liquids
    "water": WaterObject,
    "lava": LavaObject,
    "bog": BogObject,
    # Interactive
    "door": DoorObject,
    "key": KeyObject,
    "skull": SkullObject,
    "fungus": FungusObject,
    "flower": FlowerObject,
    "bolt": BoltObject,
    "pillar": PillarObject,
    "box": BoxObject,
    # Mechanical
    "belt": BeltObject,
    # Creatures
    "bug": BugObject,
    "foliage": FoliageObject,
    "algae": AlgaeObject,
    "jelly": JellyObject,
    "bat": BatObject,
    "bubble": BubbleObject,
    "bird": BirdObject,
    "hand": HandObject,
    # Nature
    "tree": TreeObject,
    "fruit": FruitObject,
    "rose": RoseObject,
    "love": LoveObject,
    "moon": MoonObject,
    "star": StarObject,
    "dust": DustObject,
    "ice": IceObject,
    "leaf": LeafObject,
    "husk": HuskObject,
    # Mechanical/Special
    "robot": RobotObject,
    "cog": CogObject,
    "cup": CupObject,
}

ALL_TEXT_OBJECTS = {
    # Nouns
    "text_baba": BabaTextObject,
    "text_keke": KekeTextObject,
    "text_anni": AnniTextObject,
    "text_me": MeTextObject,
    "text_wall": WallTextObject,
    "text_rock": RockTextObject,
    "text_flag": FlagTextObject,
    "text_tile": TileTextObject,
    "text_grass": GrassTextObject,
    "text_brick": BrickTextObject,
    "text_hedge": HedgeTextObject,
    "text_water": WaterTextObject,
    "text_lava": LavaTextObject,
    "text_bog": BogTextObject,
    "text_door": DoorTextObject,
    "text_key": KeyTextObject,
    "text_skull": SkullTextObject,
    "text_fungus": FungusTextObject,
    "text_flower": FlowerTextObject,
    "text_bolt": BoltTextObject,
    "text_pillar": PillarTextObject,
    "text_box": BoxTextObject,
    "text_belt": BeltTextObject,
    "text_bug": BugTextObject,
    "text_foliage": FoliageTextObject,
    "text_algae": AlgaeTextObject,
    "text_jelly": JellyTextObject,
    "text_tree": TreeTextObject,
    "text_fruit": FruitTextObject,
    "text_rose": RoseTextObject,
    "text_love": LoveTextObject,
    "text_moon": MoonTextObject,
    "text_star": StarTextObject,
    "text_dust": DustTextObject,
    "text_robot": RobotTextObject,
    "text_cog": CogTextObject,
    "text_ice": IceTextObject,
    "text_leaf": LeafTextObject,
    "text_husk": HuskTextObject,
    "text_bat": BatTextObject,
    "text_bubble": BubbleTextObject,
    "text_bird": BirdTextObject,
    "text_hand": HandTextObject,
    "text_cup": CupTextObject,
    # Properties
    "text_you": YouTextObject,
    "text_win": WinTextObject,
    "text_stop": StopTextObject,
    "text_push": PushTextObject,
    "text_sink": SinkTextObject,
    "text_defeat": DefeatTextObject,
    "text_hot": HotTextObject,
    "text_melt": MeltTextObject,
    "text_move": MoveTextObject,
    "text_tele": TeleTextObject,
    "text_open": OpenTextObject,
    "text_shut": ShutTextObject,
    "text_weak": WeakTextObject,
    "text_float": FloatTextObject,
    "text_pull": PullTextObject,
    "text_shift": ShiftTextObject,
    # Verbs
    "text_is": IsTextObject,
    "text_and": AndTextObject,
    "text_not": NotTextObject,
    # Special
    "text_all": AllTextObject,
    "text_text": TextTextObject,
    "text_level": LevelTextObject,
}
