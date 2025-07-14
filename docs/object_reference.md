# Baba Is You Object Reference

Complete list of all 120+ game objects and their properties.

## Regular Objects (44 total)

### Characters (IDs 1-4)
- **baba** (1): White character, default player
- **keke** (2): Red/pink character
- **anni** (3): Purple character
- **me** (4): Blue character

### Structures (IDs 5-11)
- **wall** (5): Brown, non-traversible
- **rock** (6): Gray, pushable
- **flag** (7): Gold, win condition
- **tile** (8): Light tan floor
- **grass** (9): Green decoration
- **brick** (10): Red, wall variant
- **hedge** (11): Dark green barrier

### Liquids (IDs 12-14)
- **water** (12): Blue, sink property
- **lava** (13): Orange/red, hot property
- **bog** (14): Olive, bog property

### Interactive (IDs 15-22)
- **door** (15): Brown, shut property
- **key** (16): Golden, open property
- **skull** (17): White, defeat property
- **fungus** (18): Purple
- **flower** (19): Pink decoration
- **bolt** (20): Yellow
- **pillar** (21): Gray structure
- **box** (22): Brown container

### Mechanical (ID 23)
- **belt** (23): Dark gray, shift property

### Creatures (IDs 24-27, 40-43)
- **bug** (24): Green creature
- **foliage** (25): Forest green
- **algae** (26): Teal
- **jelly** (27): Blue violet
- **bat** (40): Indigo flying
- **bubble** (41): Light blue
- **bird** (42): Sky blue
- **hand** (43): Flesh colored

### Nature (IDs 28-34, 37-39)
- **tree** (28): Green
- **fruit** (29): Red
- **rose** (30): Pink flower
- **love** (31): Hot pink heart
- **moon** (32): Beige celestial
- **star** (33): Yellow celestial
- **dust** (34): Tan particles
- **ice** (37): Pale blue, slip property
- **leaf** (38): Yellow green
- **husk** (39): Brown shell

### Special (IDs 35-36, 44-45)
- **robot** (35): Silver mechanical
- **cog** (36): Gray gear
- **cup** (44): Light yellow
- **cursor** (45): UI element

## Text Objects (66 total)

### Nouns (44)
All regular objects have corresponding text versions (IDs 46-89).
Format: `text_[object]` (e.g., text_baba, text_wall)

### Properties (17)
- **you** (90): Player control
- **win** (91): Victory condition  
- **stop** (92): Blocks movement
- **push** (93): Can be pushed
- **sink** (94): Destroys on contact
- **defeat** (95): Kills player
- **hot** (96): Melts ice
- **melt** (97): Destroyed by hot
- **move** (98): Auto-movement
- **shift** (99): Conveyor effect
- **shut** (100): Closed door
- **open** (101): Opens shut
- **weak** (102): Easily destroyed
- **float** (103): Over water
- **tele** (104): Teleportation
- **pull** (105): Pulled by movement

### Verbs (3)
- **is** (106): Rule creation
- **and** (107): Rule conjunction
- **not** (108): Rule negation

### Special (2)
- **empty** (111): Represents nothing
- **text** (112): Meta text reference

## Special IDs
- **0**: Empty cell
- **255**: Boundary marker

## Usage in Code

```python
from baba.all_objects import ALL_OBJECTS, ALL_TEXT_OBJECTS
from baba.registration import Registry

# Objects are automatically registered
registry = Registry()

# Create objects
baba = registry.create_instance("baba")
wall_text = registry.create_instance("wall", is_text=True)

# Check properties
if obj.traversible:
    # Can walk through
if obj.displaceable:
    # Can be pushed
```

## Color Coding
- Characters: Bright colors (white, red, purple, blue)
- Structures: Earth tones (brown, gray)
- Liquids: Blue/green shades
- Nature: Green/natural colors
- Text: Lighter versions of object colors