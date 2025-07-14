"""Loader for official Baba Is You level files."""

import copy
import struct
import zlib
from pathlib import Path
from typing import Any

from .grid import Grid
from .object_ids import get_object_name
from .registration import Registry


class LevelLoader:
    """Loads official Baba Is You level files (.l and .ld)."""

    # Use the comprehensive object ID mappings from object_ids.py

    def __init__(self, game_path: Path | None = None):
        """
        Initialize the level loader.

        Args:
            game_path: Path to Baba Is You installation. If None, uses default Steam location.
        """
        if game_path is None:
            game_path = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Steam"
                / "steamapps"
                / "common"
                / "Baba Is You"
            )

        self.game_path = Path(game_path)
        self.data_path = self.game_path / "Baba Is You.app" / "Contents" / "Resources" / "Data"
        self.worlds_path = self.data_path / "Worlds"

    def has_steam_levels(self) -> bool:
        """Check if Steam levels are available."""
        return self.worlds_path.exists() and self.worlds_path.is_dir()

    def read_chunks(self, data: bytes) -> dict[str, list[bytes]]:
        """Read chunk-based file format."""
        print("\n=== read_chunks debug ===")
        print(f"File size: {len(data)} bytes")
        print(f"First 20 bytes: {data[:20].hex() if len(data) >= 20 else data.hex()}")

        chunks = {}
        pos = 0

        # Skip ACHTUNG! header and version if present
        if data.startswith(b"ACHTUNG!"):
            # ACHTUNG! is 8 bytes, followed by version info
            # Let's check where the first valid chunk starts
            for test_pos in [10, 11, 12, 13]:
                if test_pos + 4 <= len(data):
                    test_chunk = data[test_pos : test_pos + 4]
                    if test_chunk in [b"MAP ", b" PAM", b"LAYR", b"RYAL"]:
                        pos = test_pos
                        print(
                            f"Found ACHTUNG! header, skipping {pos} bytes (found {test_chunk} chunk)"
                        )
                        break
            else:
                # Default to 10 if no chunk found
                pos = 10
                print("Found ACHTUNG! header, defaulting to skip 10 bytes")

        chunk_count = 0
        while pos < len(data) - 8:
            # Read chunk ID (4 bytes) and size (4 bytes)
            chunk_id_raw = data[pos : pos + 4]
            # Try to decode as ASCII - chunk IDs should be readable text
            chunk_id = chunk_id_raw.decode("ascii", errors="ignore")

            # If the chunk ID isn't printable ASCII, try reversing byte order
            if not all(32 <= ord(c) <= 126 for c in chunk_id if c):
                # Try big-endian interpretation
                chunk_id_reversed = chunk_id_raw[::-1].decode("ascii", errors="ignore")
                if all(32 <= ord(c) <= 126 for c in chunk_id_reversed if c):
                    chunk_id = chunk_id_reversed
                    chunk_id_raw = chunk_id_raw[::-1]

            chunk_id = chunk_id.strip()
            chunk_size = struct.unpack("<I", data[pos + 4 : pos + 8])[0]

            if chunk_count < 5:  # Log first few chunks
                print(f"\nChunk {chunk_count} at pos {pos}:")
                print(f"  ID (raw): {chunk_id_raw.hex()} = '{chunk_id}'")
                print(f"  Size: {chunk_size} bytes")
                print(f"  Bytes at pos: {data[pos : pos + 16].hex()}")

            # Sanity check chunk size
            if chunk_size > len(data) - pos - 8:
                print(f"  Chunk size too large! {chunk_size} > {len(data) - pos - 8}")
                break

            # Sometimes chunk IDs are reversed
            if chunk_id[::-1] in ["MAP ", "LAYR"]:
                old_id = chunk_id
                chunk_id = chunk_id[::-1]
                if chunk_count < 5:
                    print(f"  Reversed chunk ID: '{old_id}' -> '{chunk_id}'")

            # Read chunk data
            chunk_data = data[pos + 8 : pos + 8 + chunk_size]

            if chunk_id not in chunks:
                chunks[chunk_id] = []
            chunks[chunk_id].append(chunk_data)

            pos += 8 + chunk_size
            chunk_count += 1

        print(f"\nTotal chunks read: {chunk_count}")
        print(f"Unique chunk types: {list(chunks.keys())}")

        return chunks

    def decompress_level_data(self, compressed_data: bytes) -> dict[str, Any]:
        """Decompress and parse level data."""
        print("\n=== decompress_level_data debug ===")
        print(f"Input data length: {len(compressed_data)} bytes")
        print(
            f"First 20 bytes (hex): {compressed_data[:20].hex() if len(compressed_data) >= 20 else compressed_data.hex()}"
        )
        print(f"First 20 bytes (repr): {repr(compressed_data[:20])}")

        # Look for MAIN or MAINZ chunks within the data
        pos = 0
        main_chunks_found = []

        while pos < len(compressed_data) - 8:
            # Check for MAIN or MAINZ chunk
            chunk_id = compressed_data[pos : pos + 4]
            chunk_id_5 = compressed_data[pos : pos + 5] if pos < len(compressed_data) - 5 else b""

            found_chunk = False
            chunk_type = None
            chunk_data_offset = 8  # Default for MAIN

            # Check MAINZ first since MAIN is a prefix of MAINZ
            if chunk_id_5 in [b"MAINZ", b"ZNIAM"]:
                found_chunk = True
                chunk_type = chunk_id_5
                chunk_data_offset = 8  # MAINZ: 5 byte header + 3 bytes before data
            elif chunk_id in [b"MAIN", b"NIAM"]:
                found_chunk = True
                chunk_type = chunk_id
                chunk_data_offset = 8  # MAIN has 4 byte header + 4 byte size

            if found_chunk:
                # Debug: print what we're looking at
                if pos == 43:  # Special debug for position 43
                    print("\n  DEBUG at pos 43:")
                    print(
                        f"    chunk_id (4 bytes): {chunk_id.hex()} = '{chunk_id.decode('ascii', errors='ignore')}'"
                    )
                    print(
                        f"    chunk_id_5 (5 bytes): {chunk_id_5.hex()} = '{chunk_id_5.decode('ascii', errors='ignore')}'"
                    )
                    print(f"    Is MAIN? {chunk_id in [b'MAIN', b'NIAM']}")
                    print(f"    Is MAINZ? {chunk_id_5 in [b'MAINZ', b'ZNIAM']}")

                # Read chunk size (always 4 bytes after chunk ID)
                if chunk_type in [b"MAINZ", b"ZNIAM"]:
                    # Try different interpretations
                    size_le = struct.unpack("<I", compressed_data[pos + 5 : pos + 9])[0]
                    size_be = struct.unpack(">I", compressed_data[pos + 5 : pos + 9])[0]

                    if pos == 43:  # Debug
                        print(f"    MAINZ size bytes: {compressed_data[pos + 5 : pos + 9].hex()}")
                        print(f"    Little-endian: {size_le}, Big-endian: {size_be}")
                        print(f"    Context: {compressed_data[pos : pos + 20].hex()}")

                        # Check if the next byte after MAINZ might be the size
                        alt_size = compressed_data[pos + 5] if pos + 5 < len(compressed_data) else 0
                        print(f"    Single byte size: {alt_size}")

                    # Use the more reasonable size
                    chunk_size = size_be if size_be < 10000 else size_le
                else:
                    chunk_size = struct.unpack("<I", compressed_data[pos + 4 : pos + 8])[0]

                main_chunks_found.append(
                    {
                        "id": chunk_type,
                        "pos": pos,
                        "size": chunk_size,
                        "valid_size": chunk_size <= len(compressed_data) - pos - chunk_data_offset,
                    }
                )
                print(f"\nFound {chunk_type} chunk at position {pos}:")
                print(f"  Chunk size: {chunk_size} bytes")
                print(
                    f"  Valid size: {chunk_size <= len(compressed_data) - pos - chunk_data_offset}"
                )

                if chunk_size <= len(compressed_data) - pos - chunk_data_offset:
                    chunk_data = compressed_data[
                        pos + chunk_data_offset : pos + chunk_data_offset + chunk_size
                    ]
                    print(
                        f"  Chunk data first 20 bytes: {chunk_data[:20].hex() if len(chunk_data) >= 20 else chunk_data.hex()}"
                    )

                    # Debug: For MAINZ at pos 43, show what's around
                    if pos == 43 and chunk_type == b"MAINZ":
                        print("  Data around MAINZ:")
                        print(f"    pos+0 to pos+20: {compressed_data[pos : pos + 20].hex()}")
                        print(f"    pos+5 to pos+25: {compressed_data[pos + 5 : pos + 25].hex()}")
                        print(f"    pos+8 to pos+28: {compressed_data[pos + 8 : pos + 28].hex()}")
                        print(f"    pos+9 to pos+29: {compressed_data[pos + 9 : pos + 29].hex()}")
                        print(f"    pos+10 to pos+30: {compressed_data[pos + 10 : pos + 30].hex()}")

                        # Find where 7801 appears
                        for i in range(20):
                            if (
                                pos + i + 1 < len(compressed_data)
                                and compressed_data[pos + i : pos + i + 2] == b"\x78\x01"
                            ):
                                print(f"  Found zlib header 7801 at offset +{i}")

                    # Try to decompress if it looks like zlib data
                    if chunk_data[:2] in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
                        print(f"  Detected zlib header: {chunk_data[:2].hex()}")
                        try:
                            decompressed = zlib.decompress(chunk_data)
                            print(f"  Successfully decompressed to {len(decompressed)} bytes")
                            print(
                                f"  Decompressed first 20 bytes: {decompressed[:20].hex() if len(decompressed) >= 20 else decompressed.hex()}"
                            )
                            result = self.parse_level_grid(decompressed)
                            print(
                                f"  Parse result: width={result['width']}, height={result['height']}, objects={len(result['objects'])}"
                            )
                            if result["width"] > 0:
                                return result
                        except Exception as e:
                            print(f"  Decompression failed: {type(e).__name__}: {e}")
                    else:
                        # Try parsing uncompressed
                        print("  No zlib header detected, trying uncompressed parse")
                        result = self.parse_level_grid(chunk_data)
                        print(
                            f"  Parse result: width={result['width']}, height={result['height']}, objects={len(result['objects'])}"
                        )
                        if result["width"] > 0:
                            return result

            pos += 1

        print(f"\nTotal MAIN/MAINZ chunks found: {len(main_chunks_found)}")
        for chunk_info in main_chunks_found:
            print(f"  {chunk_info['id']} at pos {chunk_info['pos']}, size {chunk_info['size']}")

        # Check for data after all MAIN chunks
        if main_chunks_found:
            last_chunk = main_chunks_found[-1]
            last_pos = last_chunk["pos"] + 8 + last_chunk["size"]  # 8 bytes for header
            if last_chunk["id"] in [b"MAINZ", b"ZNIAM"]:
                last_pos = last_chunk["pos"] + 9 + last_chunk["size"]  # 9 bytes for MAINZ header

            remaining = len(compressed_data) - last_pos
            if remaining > 0:
                print(f"\n!!! Found {remaining} bytes after last MAIN chunk at pos {last_pos}")
                print(f"Next 100 bytes: {compressed_data[last_pos : last_pos + 100].hex()}")

                # Look for patterns
                # Check if it starts with DATA chunk
                if remaining >= 8 and compressed_data[last_pos : last_pos + 4] == b"DATA":
                    print("Found DATA chunk!")
                    data_size = struct.unpack("<I", compressed_data[last_pos + 4 : last_pos + 8])[0]
                    print(f"DATA chunk size: {data_size}")

                    if data_size <= remaining - 8:
                        data_chunk = compressed_data[last_pos + 8 : last_pos + 8 + data_size]
                        print(f"DATA chunk first 20 bytes: {data_chunk[:20].hex()}")

                        # Check if DATA chunk is compressed
                        if data_chunk[:2] in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
                            print("DATA chunk is zlib compressed")
                            try:
                                decompressed_data = zlib.decompress(data_chunk)
                                print(f"Decompressed DATA to {len(decompressed_data)} bytes")
                                print(f"First 100 bytes: {decompressed_data[:100].hex()}")

                                # Parse object data
                                # First 2 bytes might be object count
                                if len(decompressed_data) >= 2:
                                    obj_count = struct.unpack("<H", decompressed_data[0:2])[0]
                                    print(f"Object count: {obj_count}")

                                    if 1 <= obj_count <= 1000:
                                        objects = []
                                        pos = 2

                                        # Try different object formats
                                        # Format 1: ID (2 bytes) + X (1 byte) + Y (1 byte) + layer (1 byte)
                                        bytes_per_obj = 5

                                        if len(decompressed_data) >= 2 + (
                                            obj_count * bytes_per_obj
                                        ):
                                            print(f"Parsing {obj_count} objects (5 bytes each)")
                                            for i in range(obj_count):
                                                if pos + bytes_per_obj <= len(decompressed_data):
                                                    obj_id = struct.unpack(
                                                        "<H", decompressed_data[pos : pos + 2]
                                                    )[0]
                                                    x = decompressed_data[pos + 2]
                                                    y = decompressed_data[pos + 3]
                                                    layer = decompressed_data[pos + 4]
                                                    objects.append(
                                                        {
                                                            "id": obj_id,
                                                            "x": x,
                                                            "y": y,
                                                            "layer": layer,
                                                        }
                                                    )
                                                    if i < 10:  # Print first few
                                                        print(
                                                            f"  Object {i}: ID={obj_id}, pos=({x},{y}), layer={layer}"
                                                        )
                                                    pos += bytes_per_obj

                                            if objects:
                                                return {
                                                    "width": 12,  # From LAYR header
                                                    "height": 12,
                                                    "objects": objects,
                                                }
                                        else:
                                            # Try 4 bytes per object
                                            bytes_per_obj = 4
                                            if len(decompressed_data) >= 2 + (
                                                obj_count * bytes_per_obj
                                            ):
                                                print(f"Parsing {obj_count} objects (4 bytes each)")
                                                pos = 2
                                                for i in range(obj_count):
                                                    if pos + bytes_per_obj <= len(
                                                        decompressed_data
                                                    ):
                                                        obj_id = struct.unpack(
                                                            "<H", decompressed_data[pos : pos + 2]
                                                        )[0]
                                                        x = decompressed_data[pos + 2]
                                                        y = decompressed_data[pos + 3]
                                                        objects.append(
                                                            {"id": obj_id, "x": x, "y": y}
                                                        )
                                                        if i < 10:  # Print first few
                                                            print(
                                                                f"  Object {i}: ID={obj_id}, pos=({x},{y})"
                                                            )
                                                        pos += bytes_per_obj

                                                if objects:
                                                    return {
                                                        "width": 12,  # From LAYR header
                                                        "height": 12,
                                                        "objects": objects,
                                                    }
                            except Exception as e:
                                print(f"Failed to decompress DATA chunk: {e}")
                        else:
                            print("DATA chunk is not compressed")
                            # Check what's after DATA chunk
                            data_end = last_pos + 8 + data_size
                            if data_end < len(compressed_data):
                                next_remaining = len(compressed_data) - data_end
                                print(f"\nFound {next_remaining} bytes after DATA chunk")
                                print(
                                    f"Next 100 bytes: {compressed_data[data_end : data_end + 100].hex()}"
                                )

                                # The actual object data might be here
                                # First check if there's a size field
                                if next_remaining >= 4:
                                    next_size = struct.unpack(
                                        "<I", compressed_data[data_end : data_end + 4]
                                    )[0]
                                    print(f"Next chunk size: {next_size}")

                                    if next_size <= next_remaining - 4:
                                        next_data = compressed_data[
                                            data_end + 4 : data_end + 4 + next_size
                                        ]
                                        if next_data[:2] in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
                                            print("Found zlib compressed object data!")
                                            try:
                                                obj_data = zlib.decompress(next_data)
                                                print(f"Decompressed to {len(obj_data)} bytes")
                                                print(f"First 100 bytes: {obj_data[:100].hex()}")

                                                # Parse this as object data
                                                # Looking at the data, it seems to be a grid of object IDs
                                                # 700 bytes for 12x12 grid = ~4.86 bytes per cell
                                                # Let's assume it's multiple layers

                                                print("Parsing as grid data...")
                                                width, height = 12, 12  # From LAYR header

                                                # Calculate layers based on data size
                                                bytes_per_layer = width * height
                                                num_layers = len(obj_data) // bytes_per_layer
                                                remainder = len(obj_data) % bytes_per_layer
                                                print(
                                                    f"Grid: {width}x{height}, {num_layers} complete layers, {remainder} extra bytes"
                                                )
                                                print(
                                                    f"Total bytes: {len(obj_data)}, bytes per layer: {bytes_per_layer}"
                                                )

                                                objects = []

                                                # Parse each layer
                                                for layer in range(num_layers):
                                                    layer_start = layer * bytes_per_layer
                                                    layer_data = obj_data[
                                                        layer_start : layer_start + bytes_per_layer
                                                    ]

                                                    print(f"\nLayer {layer}:")
                                                    # Print first few rows of each layer
                                                    for y in range(min(3, height)):  # First 3 rows
                                                        row_str = ""
                                                        for x in range(min(12, width)):
                                                            idx = y * width + x
                                                            if idx < len(layer_data):
                                                                row_str += f"{layer_data[idx]:3d} "
                                                        print(f"  Row {y}: {row_str}")

                                                    # Extract objects from this layer
                                                    for y in range(height):
                                                        for x in range(width):
                                                            idx = y * width + x
                                                            if idx < len(layer_data):
                                                                obj_id = layer_data[idx]
                                                                if obj_id > 0:  # 0 = empty
                                                                    objects.append(
                                                                        {
                                                                            "id": obj_id,
                                                                            "x": x,
                                                                            "y": y,
                                                                            "layer": layer,
                                                                        }
                                                                    )

                                                print(f"\nTotal objects found: {len(objects)}")
                                                if objects:
                                                    # Print first few objects
                                                    for i, obj in enumerate(objects[:10]):
                                                        print(
                                                            f"  Object {i}: ID={obj['id']}, pos=({obj['x']},{obj['y']}), layer={obj['layer']}"
                                                        )

                                                    return {
                                                        "width": width,
                                                        "height": height,
                                                        "objects": objects,
                                                    }
                                            except Exception as e:
                                                print(f"Failed to decompress: {e}")

        # Fallback: try direct decompression
        print("\nTrying fallback direct decompression...")
        if compressed_data[:2] in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
            print(f"Detected zlib header in raw data: {compressed_data[:2].hex()}")
            try:
                decompressed = zlib.decompress(compressed_data)
                print(f"Successfully decompressed to {len(decompressed)} bytes")
                result = self.parse_level_grid(decompressed)
                print(
                    f"Parse result: width={result['width']}, height={result['height']}, objects={len(result['objects'])}"
                )
                return result
            except Exception as e:
                print(f"Decompression failed: {type(e).__name__}: {e}")
        else:
            print("No zlib header detected in raw data")

        # Try parsing the raw data directly
        print("\nTrying to parse raw data as uncompressed grid...")
        result = self.parse_level_grid(compressed_data)
        print(
            f"Parse result: width={result['width']}, height={result['height']}, objects={len(result['objects'])}"
        )

        if result["width"] == 0:
            print("\n!!! Failed to parse level data !!!")

        return result

    def parse_level_grid(self, data: bytes) -> dict[str, Any]:
        """Parse the decompressed level grid data."""
        print("\n  === parse_level_grid debug ===")
        print(f"  Data length: {len(data)} bytes")
        print(f"  First 100 bytes (hex): {data[:100].hex() if len(data) >= 100 else data.hex()}")

        result = {"width": 0, "height": 0, "objects": []}

        # The decompressed data might not have dimensions at the start
        # Let's check if the data looks like raw grid data
        # Based on the LAYR header, we know it's 12x12 = 144 cells
        # Each cell might have multiple layers

        # First, let's try parsing as if dimensions are at the start
        if len(data) >= 8:
            width = struct.unpack("<I", data[0:4])[0]
            height = struct.unpack("<I", data[4:8])[0]
            print(f"  Parsed dimensions (assuming header): {width}x{height}")
            print(f"  Raw dimension bytes: width={data[0:4].hex()}, height={data[4:8].hex()}")

            # Sanity check dimensions
            if 1 <= width <= 100 and 1 <= height <= 100:
                result["width"] = width
                result["height"] = height

                # Calculate expected data size (7-9 bytes per cell)
                expected_size = width * height * 7
                print(f"  Expected data size: {expected_size} bytes (for 7 bytes per cell)")
                print(f"  Actual data size: {len(data) - 8} bytes (excluding header)")

                if len(data) >= 8 + expected_size:
                    # Parse grid data
                    pos = 8
                    object_count = 0
                    for y in range(height):
                        for x in range(width):
                            # Each cell can have multiple objects (7-9 bytes)
                            cell_data = data[pos : pos + 7]

                            # Parse objects in this cell
                            for i in range(0, len(cell_data), 1):
                                obj_id = cell_data[i]
                                if obj_id > 0 and obj_id != 255:  # 0=empty, 255=special
                                    result["objects"].append({"id": obj_id, "x": x, "y": y})
                                    object_count += 1
                                    if object_count <= 5:  # Log first few objects
                                        print(f"    Found object ID {obj_id} at ({x}, {y})")

                            pos += 7
                            if pos >= len(data):
                                break
                        if pos >= len(data):
                            break
                    print(f"  Total objects found: {len(result['objects'])}")
                else:
                    print(
                        f"  Not enough data for grid! Need {8 + expected_size} bytes, have {len(data)}"
                    )
            else:
                print(f"  Invalid dimensions: {width}x{height} (must be 1-100)")
        else:
            print(f"  Not enough data for header! Need 8 bytes, have {len(data)}")

        # Alternative parsing: assume no header and data is raw grid
        if result["width"] == 0 and len(data) > 0:
            print("\n  Trying alternative parsing (no header, raw grid data)...")
            # Common grid sizes based on data length
            # For 12x12 grid with multiple layers, we might have different data sizes
            possible_sizes = [
                (12, 12),  # From LAYR header
                (15, 10),
                (10, 10),
                (20, 15),
                (16, 16),
            ]

            for w, h in possible_sizes:
                # Each cell might have 1 object ID (2 bytes) or multiple layers
                for bytes_per_cell in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    expected = w * h * bytes_per_cell
                    if len(data) == expected:
                        print(f"    Found match: {w}x{h} with {bytes_per_cell} bytes per cell")
                        result["width"] = w
                        result["height"] = h

                        # Parse the grid
                        pos = 0
                        for y in range(h):
                            for x in range(w):
                                for _layer in range(bytes_per_cell):
                                    if pos < len(data):
                                        obj_id = data[pos]
                                        if obj_id > 0 and obj_id != 255:
                                            result["objects"].append({"id": obj_id, "x": x, "y": y})
                                        pos += 1

                        print(f"    Found {len(result['objects'])} objects")
                        return result

        return result

    def load_level_metadata(self, ld_path: Path) -> dict[str, Any]:
        """Load level metadata from .ld file."""
        metadata = {
            "name": "",
            "subtitle": "",
            "author": "",
            "palette": "",
            "music": "",
            "width": 0,
            "height": 0,
            "custom_objects": {},
        }

        if not ld_path.exists():
            return metadata

        current_section = None
        with open(ld_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                elif "=" in line and current_section:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if current_section == "general":
                        if key == "name":
                            metadata["name"] = value
                        elif key == "subtitle":
                            metadata["subtitle"] = value
                        elif key == "author":
                            metadata["author"] = value
                        elif key == "palette":
                            metadata["palette"] = value
                        elif key == "music":
                            metadata["music"] = value
                        elif key == "width":
                            metadata["width"] = int(value)
                        elif key == "height":
                            metadata["height"] = int(value)

        return metadata

    def load_level(self, world: str, level_num: int, registry: Registry) -> Grid | None:
        """
        Load a level from the official game files.

        Args:
            world: World name (e.g., 'baba', 'new_adv', 'museum')
            level_num: Level number
            registry: Object registry for creating game objects

        Returns:
            Grid object with the loaded level, or None if loading fails
        """
        level_name = f"{level_num}level"
        l_path = self.worlds_path / world / f"{level_name}.l"
        ld_path = self.worlds_path / world / f"{level_name}.ld"

        if not l_path.exists():
            print(f"Level file not found: {l_path}")
            return None

        # Load metadata
        metadata = self.load_level_metadata(ld_path)

        # Read level data
        with open(l_path, "rb") as f:
            level_data = f.read()

        # Parse chunks
        chunks = self.read_chunks(level_data)

        print(f"\n=== Loading level {level_name} ===")
        print(f"Level file size: {len(level_data)} bytes")
        print(f"Chunks found: {list(chunks.keys())}")
        for chunk_type, chunk_list in chunks.items():
            print(f"  {chunk_type}: {len(chunk_list)} chunk(s)")
            for i, chunk in enumerate(chunk_list):
                print(f"    Chunk {i}: {len(chunk)} bytes")

        # Find and decompress level data from LAYR chunks
        level_info = None
        if "LAYR" in chunks:
            print(f"\nProcessing {len(chunks['LAYR'])} LAYR chunk(s)...")
            for idx, chunk_data in enumerate(chunks["LAYR"]):
                print(f"\nLAYR chunk {idx}:")
                print(f"  Length: {len(chunk_data)} bytes")
                print(
                    f"  First 20 bytes: {chunk_data[:20].hex() if len(chunk_data) >= 20 else chunk_data.hex()}"
                )

                # Extract dimensions from LAYR header
                if len(chunk_data) >= 13:
                    width = chunk_data[10]
                    height = chunk_data[12]
                    print(f"  Dimensions from LAYR header: {width}x{height}")
                    print(f"  Header bytes 10-13: {chunk_data[10:14].hex()}")

                    # Try to decompress the level data
                    result = self.decompress_level_data(chunk_data)
                    if result["width"] > 0:
                        level_info = result
                        print("  Successfully parsed level data!")
                        break
                    elif width > 0 and height > 0:
                        # Use dimensions from LAYR header if parsing failed
                        print("  Using fallback dimensions from LAYR header")
                        level_info = {"width": width, "height": height, "objects": []}
                else:
                    print(f"  LAYR chunk too small ({len(chunk_data)} bytes)")
        else:
            print("\nNo LAYR chunks found!")

        if not level_info:
            print(f"\n!!! Could not parse level data for {level_name} !!!")
            return None

        # Use metadata dimensions if available
        if metadata["width"] > 0:
            level_info["width"] = metadata["width"]
        if metadata["height"] > 0:
            level_info["height"] = metadata["height"]

        # Create grid
        grid = Grid(level_info["width"], level_info["height"], registry)

        # Place objects
        missing_objects = set()
        placed_count = 0

        # No longer need substitutions since we have all objects!

        for obj_data in level_info["objects"]:
            obj_name = get_object_name(obj_data["id"])
            if obj_name and obj_name != "empty":
                # Check if it's a text object
                is_text = obj_name.startswith("text_")

                if is_text:
                    # Strip 'text_' prefix for text object lookup
                    base_name = obj_name[5:]  # Remove 'text_' prefix

                    # Try to create text object
                    obj = registry.create_instance(base_name, is_text=True)
                    if obj:
                        grid.place_object(obj, obj_data["x"], obj_data["y"])
                        placed_count += 1
                    else:
                        missing_objects.add(obj_name)
                else:
                    # No substitution needed - we have all objects

                    if obj_name in registry.objects:
                        # Create a copy of the registered object
                        template_obj = registry.objects[obj_name]
                        obj = copy.deepcopy(template_obj)
                        grid.place_object(obj, obj_data["x"], obj_data["y"])
                        placed_count += 1
                    else:
                        missing_objects.add(obj_name)

        if missing_objects:
            print(f"\nWarning: {len(missing_objects)} object types not in registry:")
            for name in sorted(missing_objects):
                print(f"  - {name}")
        print(f"\nPlaced {placed_count} out of {len(level_info['objects'])} objects")

        return grid

    def list_worlds(self) -> list[str]:
        """List all available worlds."""
        if not self.worlds_path.exists():
            return []
        return [d.name for d in self.worlds_path.iterdir() if d.is_dir()]

    def list_levels(self, world: str) -> list[int]:
        """List all level numbers in a world."""
        world_path = self.worlds_path / world
        if not world_path.exists():
            return []

        levels = []
        for file in world_path.glob("*level.l"):
            try:
                level_num = int(file.stem.replace("level", ""))
                levels.append(level_num)
            except ValueError:
                continue

        return sorted(levels)
