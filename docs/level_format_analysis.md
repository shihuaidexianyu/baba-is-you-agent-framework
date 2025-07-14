# Baba Is You Level Format

## File Types
- `.l`: Binary level data
- `.ld`: INI-format metadata

## .l File Structure

### Header
- Magic: `ACHTUNG!` (8 bytes)
- Version: 0x05 0x01 (2 bytes)

### Chunks
Format: ID (4 bytes) + size (4 bytes) + data

Common chunks:
- **MAP**: Map metadata (2 bytes)
- **LAYR**: Level data
  - Header (16 bytes): dimensions and properties
  - Sub-chunks: MAIN/MAINZ (compressed grid data)

### LAYR Header
- Bytes 10-11: Width
- Bytes 12-13: Height
- Other bytes: layer ID, flags, object count

### Compression
- zlib (headers: 0x78 0x01, 0x78 0x9c, 0x78 0xda)
- Decompressed data: grid of object IDs
- Special values: 0 (empty), 255 (boundary)

## .ld File Structure

INI format with [general] section:
- `name`: Display name
- `author`: Creator
- `palette`: Color scheme
- `music`: Track name
- `subtitle`: Description
- Other game-specific settings

## Reading Process

1. Verify ACHTUNG! header
2. Skip version bytes
3. Parse chunks sequentially
4. Extract dimensions from LAYR
5. Decompress MAIN chunks
6. Map IDs to objects

## Notes
- Multiple MAIN chunks = multiple layers
- Chunk IDs sometimes reversed (LAYR/RYAL)
- Grid stored in row-major order