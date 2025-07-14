#!/usr/bin/env python3
"""
Setup script to copy Baba Is You sprites from Steam installation.
Only run this if you own a legal copy of Baba Is You.
"""

import platform
import shutil
import sys
from pathlib import Path


def find_steam_sprites():
    """Find Baba Is You sprite directory based on platform."""
    system = platform.system()

    possible_paths = []

    if system == "Darwin":  # macOS
        possible_paths = [
            Path.home()
            / "Library/Application Support/Steam/steamapps/common/Baba Is You/Baba Is You.app/Contents/Resources/Data/Sprites",
            Path("/Applications/Baba Is You.app/Contents/Resources/Data/Sprites"),
        ]
    elif system == "Windows":
        possible_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Baba Is You/Data/Sprites"),
            Path("C:/Program Files/Steam/steamapps/common/Baba Is You/Data/Sprites"),
            Path.home() / "Steam/steamapps/common/Baba Is You/Data/Sprites",
        ]
    elif system == "Linux":
        possible_paths = [
            Path.home() / ".steam/steam/steamapps/common/Baba Is You/Data/Sprites",
            Path.home() / ".local/share/Steam/steamapps/common/Baba Is You/Data/Sprites",
        ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def main():
    """Copy sprites from Steam to project directory."""
    print("Baba Is You Sprite Setup")
    print("=" * 40)
    print("This script copies sprites from your Baba Is You installation.")
    print("Only run this if you legally own the game!")
    print()

    # Find source directory
    source_dir = find_steam_sprites()

    if not source_dir:
        print("❌ Could not find Baba Is You installation.")
        print("\nPlease make sure:")
        print("1. You have Baba Is You installed via Steam")
        print("2. Steam is installed in the default location")
        print("\nYou can also manually copy sprites from:")
        print("  macOS: ~/Library/Application Support/Steam/steamapps/common/Baba Is You/...")
        print("  Windows: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Baba Is You\\...")
        print("  Linux: ~/.steam/steam/steamapps/common/Baba Is You/...")
        return 1

    print(f"✓ Found Baba Is You sprites at: {source_dir}")

    # Count sprites
    png_files = list(source_dir.glob("*.png"))
    print(f"  Found {len(png_files)} sprite files")

    # Get destination
    script_dir = Path(__file__).parent
    dest_dir = script_dir.parent / "baba" / "assets" / "sprites"

    # Create directory if needed
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Ask for confirmation
    print(f"\nThis will copy sprites to: {dest_dir}")
    response = input("Continue? (y/n): ").lower().strip()

    if response != "y":
        print("Cancelled.")
        return 0

    # Copy files
    print("\nCopying sprites...")
    copied = 0

    for png_file in png_files:
        dest_file = dest_dir / png_file.name
        try:
            shutil.copy2(png_file, dest_file)
            copied += 1
            if copied % 100 == 0:
                print(f"  Copied {copied}/{len(png_files)} files...")
        except Exception as e:
            print(f"  Warning: Failed to copy {png_file.name}: {e}")

    print(f"\n✓ Successfully copied {copied} sprite files!")
    print("\nYou can now run the game with official sprites.")
    print("Remember: These sprites should NOT be committed to git!")

    # Create a marker file
    marker_file = dest_dir / ".has_official_sprites"
    marker_file.write_text(
        "This directory contains official Baba Is You sprites.\nDO NOT COMMIT TO GIT!"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
