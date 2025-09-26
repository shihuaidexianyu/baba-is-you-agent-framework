"""Loader for official Baba Is You level files from a local directory (map/)."""

import copy
import struct
import zlib
from pathlib import Path
from typing import Any

from .grid import Grid
from .object_ids import get_object_name
from .registration import Registry


class LevelLoader:
    """Loads official Baba Is You level files (.l and .ld) from a local folder.

    仅支持平铺在根目录：map/<level_name>.l 与可选 map/<level_name>.ld
    """

    # Use the comprehensive object ID mappings from object_ids.py

    def __init__(self, worlds_path: Path | str = "map"):
        """Initialize with a local worlds root directory (default: ./map)."""
        self.worlds_path = Path(worlds_path)

    # Removed Steam/installation probing; only local worlds_path is supported

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
        """Decompress and parse level data - find MAIN chunks with diverse object data."""
        print("\n=== decompress_level_data debug ===")
        print(f"Input data length: {len(compressed_data)} bytes")
        
        # Extract dimensions from LAYR header (bytes 10 and 12)
        width = height = 12  # Default
        if len(compressed_data) >= 14:
            width = compressed_data[10]  
            height = compressed_data[12]
            print(f"Grid dimensions from LAYR header: {width}x{height}")

        # Look for MAIN chunks (not MAINZ) - they contain the object data
        pos = 0
        main_chunks = []
        
        while pos < len(compressed_data) - 8:
            if compressed_data[pos:pos+4] == b"MAIN":
                size = struct.unpack("<I", compressed_data[pos+4:pos+8])[0]
                if pos + 8 + size <= len(compressed_data):
                    main_data = compressed_data[pos+8:pos+8+size]
                    main_chunks.append((pos, size, main_data))
                    print(f"Found MAIN chunk at {pos}, size {size}")
                pos += 8 + size
            else:
                pos += 1
        
        if not main_chunks:
            print("No MAIN chunks found")
            return {"width": width, "height": height, "objects": []}
        
        # Try each MAIN chunk to find the one with object data
        for chunk_pos, chunk_size, chunk_data in main_chunks:
            print(f"\nTrying MAIN chunk at {chunk_pos}")
            
            # Verify it's zlib compressed
            if chunk_data[:2] not in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
                print(f"Not zlib compressed (header: {chunk_data[:2].hex()})")
                continue
                
            # Decompress MAIN data
            try:
                main_decompressed = zlib.decompress(chunk_data)
                unique_vals = sorted(set(main_decompressed))
                print(f"Decompressed to {len(main_decompressed)} bytes")
                print(f"Unique values: {unique_vals}")
                
                # Check if this looks like object data (diverse IDs, not just boundary)
                non_boundary_vals = [v for v in unique_vals if v not in (0, 255)]
                if len(non_boundary_vals) >= 3:  # Need at least 3 different object types
                    print(f"This MAIN chunk contains diverse object data")
                    
                    # Parse decompressed data as object grid 
                    objects = []
                    cells_per_layer = width * height
                    
                    if cells_per_layer == 0:
                        print("Invalid grid dimensions")
                        continue
                    
                    # Calculate number of layers
                    num_layers = len(main_decompressed) // cells_per_layer
                    remainder = len(main_decompressed) % cells_per_layer
                    
                    print(f"Parsing grid: {width}x{height}, {num_layers} complete layers, {remainder} extra bytes")
                    
                    # Parse each layer
                    for layer in range(num_layers):
                        layer_start = layer * cells_per_layer
                        layer_end = layer_start + cells_per_layer
                        layer_data = main_decompressed[layer_start:layer_end]
                        
                        layer_objects = 0
                        
                        # Parse each cell in row-major order
                        for i, obj_id in enumerate(layer_data):
                            if obj_id > 0 and obj_id != 255:  # 0 = empty, 255 = boundary
                                # Convert linear index to (x, y) coordinates
                                y = i // width
                                x = i % width
                                
                                objects.append({
                                    "id": obj_id,
                                    "x": x,
                                    "y": y,
                                    "layer": layer
                                })
                                layer_objects += 1
                        
                        print(f"Layer {layer}: {layer_objects} objects, unique IDs: {sorted(set(layer_data))}")
                    
                    print(f"Total objects found: {len(objects)}")
                    
                    # Show first few objects for debugging
                    if objects:
                        print("First 10 objects:")
                        for i, obj in enumerate(objects[:10]):
                            from .object_ids import get_object_name
                            name = get_object_name(obj['id'])
                            print(f"  {i}: {name}(ID={obj['id']}) at ({obj['x']},{obj['y']}) layer={obj['layer']}")
                    
                    return {"width": width, "height": height, "objects": objects}
                    
            except Exception as e:
                print(f"Failed to decompress MAIN data: {e}")
                continue
        
        print("No valid object data found in any MAIN chunk")
        return {"width": width, "height": height, "objects": []}

        # Old complex parsing logic follows (as fallback)
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

            if not found_chunk:
                pos += 1
                continue

            # Read chunk size (always 4 bytes after chunk ID)
            if chunk_type in [b"MAINZ", b"ZNIAM"]:
                # Try different interpretations
                size_le = struct.unpack("<I", compressed_data[pos + 5 : pos + 9])[0]
                size_be = struct.unpack(">I", compressed_data[pos + 5 : pos + 9])[0]
                # Use the more reasonable size
                chunk_size = size_be if size_be < 10000 else size_le
            else:
                chunk_size = struct.unpack("<I", compressed_data[pos + 4 : pos + 8])[0]

            main_chunks_found.append({
                "id": chunk_type,
                "pos": pos,
                "size": chunk_size,
                "valid_size": chunk_size <= len(compressed_data) - pos - chunk_data_offset,
            })

            pos += chunk_size + chunk_data_offset

        # Fallback to old parsing if new method didn't work
        print(f"\nFallback: Found {len(main_chunks_found)} MAIN/MAINZ chunks")
        return {"width": width, "height": height, "objects": []}

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


    # === Flat layout helpers (map root) ===
    def load_level_flat(self, level_name: str, registry: Registry) -> Grid | None:
        """Load a level when files are directly under map/.

        参数：
            level_name: 可为不带扩展的文件名（如 "1level"、"n1level"），
                        也可包含 .l/.ld 扩展（优先读取 .l）。
        返回：Grid 或 None
        """
        # 规范化：去掉扩展，只保留 stem
        name = level_name
        if name.endswith(".l") or name.endswith(".ld"):
            name = Path(name).stem

        l_path = self.worlds_path / f"{name}.l"
        ld_path = self.worlds_path / f"{name}.ld"

        if not l_path.exists():
            print(f"Level file not found: {l_path}")
            return None

        metadata = self.load_level_metadata(ld_path)

        with open(l_path, "rb") as f:
            level_data = f.read()

        chunks = self.read_chunks(level_data)
        print(f"\n=== Loading level {name} (flat) ===")
        print(f"Level file size: {len(level_data)} bytes")
        print(f"Chunks found: {list(chunks.keys())}")
        for chunk_type, chunk_list in chunks.items():
            print(f"  {chunk_type}: {len(chunk_list)} chunk(s)")
            for i, chunk in enumerate(chunk_list):
                print(f"    Chunk {i}: {len(chunk)} bytes")

        level_info = None
        if "LAYR" in chunks:
            print(f"\nProcessing {len(chunks['LAYR'])} LAYR chunk(s)...")
            for idx, chunk_data in enumerate(chunks["LAYR"]):
                print(f"\nLAYR chunk {idx}:")
                print(f"  Length: {len(chunk_data)} bytes")
                print(
                    f"  First 20 bytes: {chunk_data[:20].hex() if len(chunk_data) >= 20 else chunk_data.hex()}"
                )

                if len(chunk_data) >= 13:
                    width = chunk_data[10]
                    height = chunk_data[12]
                    print(f"  Dimensions from LAYR header: {width}x{height}")
                    print(f"  Header bytes 10-13: {chunk_data[10:14].hex()}")

                    result = self.decompress_level_data(chunk_data)
                    if result["width"] > 0:
                        level_info = result
                        print("  Successfully parsed level data!")
                        break
                    elif width > 0 and height > 0:
                        print("  Using fallback dimensions from LAYR header")
                        level_info = {"width": width, "height": height, "objects": []}
                else:
                    print(f"  LAYR chunk too small ({len(chunk_data)} bytes)")
        else:
            print("\nNo LAYR chunks found!")

        if not level_info:
            print(f"\n!!! Could not parse level data for {name} !!!")
            return None

        if metadata["width"] > 0:
            level_info["width"] = metadata["width"]
        if metadata["height"] > 0:
            level_info["height"] = metadata["height"]

        grid = Grid(level_info["width"], level_info["height"], registry)

        missing_objects = set()
        placed_count = 0

        for obj_data in level_info["objects"]:
            obj_name = get_object_name(obj_data["id"])
            if obj_name and obj_name != "empty":
                is_text = obj_name.startswith("text_")
                if is_text:
                    base_name = obj_name[5:]
                    obj = registry.create_instance(base_name, is_text=True)
                    if obj:
                        grid.place_object(obj, obj_data["x"], obj_data["y"])
                        placed_count += 1
                    else:
                        missing_objects.add(obj_name)
                else:
                    if obj_name in registry.objects:
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

    def list_level_names(self) -> list[str]:
        """列出 map 根目录中可用的关卡名（不带扩展）。"""
        if not self.worlds_path.exists():
            return []
        names = []
        for file in self.worlds_path.glob("*level.l"):
            names.append(file.stem)
        return sorted(names)

    # 删除了 world/level 分层相关的加载与列举接口
