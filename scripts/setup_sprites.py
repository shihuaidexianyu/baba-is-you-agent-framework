#!/usr/bin/env python3
"""
Helper to copy official sprites from a local Steam install to this repo.
Only run this if you legally own Baba Is You. Do NOT commit copied assets.
"""
from __future__ import annotations

import platform
import shutil
from pathlib import Path


def find_steam_sprite_dirs() -> list[Path]:
    sysname = platform.system()
    home = Path.home()
    candidates: list[Path] = []

    if sysname == "Linux":
        candidates += [
            home / ".steam/steam/steamapps/common/Baba Is You/Data/Sprites",
            home / ".local/share/Steam/steamapps/common/Baba Is You/Data/Sprites",
        ]
    elif sysname == "Darwin":
        candidates += [
            home / "Library/Application Support/Steam/steamapps/common/Baba Is You/Baba Is You.app/Contents/Resources/Data/Sprites",
            Path("/Applications/Baba Is You.app/Contents/Resources/Data/Sprites"),
        ]
    elif sysname == "Windows":
        candidates += [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Baba Is You/Data/Sprites"),
            Path("C:/Program Files/Steam/steamapps/common/Baba Is You/Data/Sprites"),
            home / "Steam/steamapps/common/Baba Is You/Data/Sprites",
        ]

    return [p for p in candidates if p.exists()]


def copy_sprites(src: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src.glob("*.png"):
        shutil.copy2(f, dest / f.name)
        count += 1
    (dest / ".has_official_sprites").write_text(
        "Official sprites copied for local use. DO NOT COMMIT.\n"
    )
    return count


def main() -> int:
    print("Searching Steam install for Baba Is You sprites...")
    found = find_steam_sprite_dirs()
    if not found:
        print("No Steam sprite folder found. If you installed to a custom path, set BABA_SPRITES_DIR and run again.")
        return 1

    # Prefer the first viable directory
    src = found[0]
    dest = Path(__file__).resolve().parents[1] / "baba" / "assets" / "sprites"
    print(f"Copying from: {src}")
    print(f"          to: {dest}")
    n = copy_sprites(src, dest)
    print(f"Copied {n} files.")
    print("You can now run with real sprites. These assets are local-only and should not be committed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
