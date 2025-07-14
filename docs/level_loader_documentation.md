# Baba Is You Level Loader

Loads official Baba Is You level files (.l and .ld) from Steam installations.

## File Locations

```
~/Library/Application Support/Steam/steamapps/common/Baba Is You/
└── Baba Is You.app/Contents/Resources/Data/Worlds/
    ├── baba/     # 249 levels
    ├── new_adv/  # 225 levels  
    ├── museum/   # 121 levels
    └── debug/    # 4 levels
```

## File Format

### Structure
- Header: `ACHTUNG!` (8 bytes) + version (5 bytes)
- Chunks: ID (4 bytes) + size (4 bytes) + data

### Key Chunks
- **MAP**: Map metadata
- **LAYR**: Level data
  - Dimensions at bytes 10 (width) and 12 (height)
  - Contains MAIN/MAINZ sub-chunks with zlib-compressed data
  - Object data follows DATA chunk

### Compression
- Standard zlib (headers: 0x78 0x01, 0x78 0x9c, 0x78 0xda)
- Multiple compressed sections per level

## Object IDs

Common objects:
- 0: empty
- 1-4: baba, keke, anni, me
- 5-7: wall, rock, flag
- 12: water
- 46+: text objects (text_baba, text_is, text_you, etc.)
- 255: boundary marker

See `baba/object_ids.py` for complete mappings (156 total).

## API Usage

```python
from baba.level_loader import LevelLoader
from baba.registration import Registry

registry = Registry()
loader = LevelLoader()
grid = loader.load_level("baba", 0, registry)
```

## Implementation

### Core Files
- `baba/level_loader.py`: Main loader
- `baba/object_ids.py`: ID mappings
- `baba/all_objects.py`: Object definitions

### Key Methods
- `read_chunks()`: Parse file format
- `decompress_level_data()`: Handle compression
- `load_level(world, level_num, registry)`: Load a level

### Data Format
- Grid stored as sequential bytes (row-major)
- Multiple layers per level
- Each cell: one object ID per layer

## Testing

```bash
pixi run test-loader           # Test loading
pixi run viz-level 30          # Visualize level 30
```

## Technical Details

- Levels have 2-4 layers
- Object data uses 7-9 bytes per cell when compressed
- LAYR chunk contains both compressed masks and object data
- Grid dimensions extracted from LAYR header

## Current Status

✅ All 120+ object types implemented
✅ Correct ID to object mapping
✅ Rule system works with text objects
✅ Levels load without substitutions