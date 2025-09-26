"""Load and manage actual Baba Is You sprites.

功能增强：
- 自动搜索多个精灵目录：
    1) 环境变量 BABA_SPRITES_DIR 指定目录
    2) 本仓库 `baba/assets/sprites`
    3) 子仓库 `baba-is-agi/baba/assets/sprites`
    4) 常见 Steam 安装路径（Linux）
- 放宽文件名匹配：
    - `<name>.png`
    - `<name>_0_1.png` 或 `<name>_<v>_<f>.png`
    - `text_<name>.png` 与 `<name>_text.png` 互通映射
- 提供 reload(new_dir=None) 与 status() 便于热重载与诊断。
"""

import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


class SpriteLoader:
    """Loads and caches actual game sprites with fallback support."""

    def __init__(self):
        # 初始化
        self.sprite_cache: dict[str, np.ndarray] = {}
        self.default_size = (24, 24)
        self.has_real_sprites = False
        self.sprite_mapping: dict[str, str] = {}

        # 选择精灵目录并扫描
        self.sprite_dir = self._pick_sprite_dir()
        self._scan_available_sprites()
        if self.sprite_mapping:
            self.has_real_sprites = True
            print(f"Detected {len(self.sprite_mapping)} sprite mappings in: {self.sprite_dir}")
        else:
            print("No game sprites found. Using custom fallback sprites.")

    # -------- 目录选择与扫描 --------
    def _candidate_dirs(self) -> list[Path]:
        """Return candidate directories to search for sprites."""
        candidates: list[Path] = []

        # 1) 环境变量
        env_dir = os.getenv("BABA_SPRITES_DIR")
        if env_dir:
            candidates.append(Path(env_dir))

        # 2) 本项目内置
        candidates.append(Path(__file__).parent / "assets" / "sprites")

        # 3) 子仓库 baba-is-agi
        candidates.append(Path(__file__).resolve().parents[1] / "baba-is-agi" / "baba" / "assets" / "sprites")

        # 4) 常见 Steam 路径（Linux）
        home = Path.home()
        candidates.extend(
            [
                home / ".steam/steam/steamapps/common/Baba Is You/Data/Sprites",
                home / ".local/share/Steam/steamapps/common/Baba Is You/Data/Sprites",
            ]
        )

        # 去重，保持顺序
        seen = set()
        uniq: list[Path] = []
        for p in candidates:
            try:
                key = p.resolve()
            except Exception:
                key = p
            if key not in seen:
                seen.add(key)
                uniq.append(p)
        return uniq

    def _pick_sprite_dir(self) -> Path:
        for d in self._candidate_dirs():
            if d.exists() and any(d.glob("*.png")):
                return d
        # 默认回退到项目 assets 目录
        return Path(__file__).parent / "assets" / "sprites"

    def _scan_available_sprites(self):
        """Scan the sprite directory and build name->filename mapping."""
        self.sprite_mapping.clear()
        d = self.sprite_dir
        if not d.exists():
            return

        def add_map(base: str, filename: str):
            key = base.lower()
            if key not in self.sprite_mapping:
                self.sprite_mapping[key] = filename

                # 文本对象互通映射：text_x <-> x_text
                if key.startswith("text_"):
                    add_map(key[5:] + "_text", filename)
                if key.endswith("_text"):
                    add_map("text_" + key[:-5], filename)

        for f in d.glob("*.png"):
            stem = f.stem
            parts = stem.split("_")

            # 形式1：<name>.png
            add_map(stem, f.name)

            # 形式2：<name>_<v>_<frame>.png（如 baba_0_1.png）
            if len(parts) >= 3 and parts[-2].isdigit() and parts[-1].isdigit():
                base = "_".join(parts[:-2])
                add_map(base, f.name)

    def load_sprite(self, name: str, size: tuple[int, int] | None = None) -> np.ndarray | None:
        """
        Load a sprite by name.

        Args:
            name: Name of the sprite
            size: Target size (width, height), uses default if None

        Returns:
            Sprite as numpy array or None if not found
        """
        if size is None:
            size = self.default_size

        # Check cache
        cache_key = f"{name}_{size[0]}x{size[1]}"
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key].copy()

        # Get sprite filename（大小写不敏感）
        sprite_file = self.sprite_mapping.get(name.lower())
        if not sprite_file:
            return None

        sprite_path = self.sprite_dir / sprite_file
        if not sprite_path.exists():
            return None

        try:
            # Load image
            img = Image.open(sprite_path)

            # Convert to RGBA if not already
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Resize using nearest neighbor to preserve pixel art
            img = img.resize(size, Image.NEAREST)

            # Convert to numpy array
            sprite = np.array(img)

            # Convert RGBA to RGB with black background
            if sprite.shape[2] == 4:
                # Create black background
                rgb_sprite = np.zeros((sprite.shape[0], sprite.shape[1], 3), dtype=np.uint8)

                # Apply alpha blending
                alpha = sprite[:, :, 3] / 255.0
                for c in range(3):
                    rgb_sprite[:, :, c] = (sprite[:, :, c] * alpha).astype(np.uint8)

                sprite = rgb_sprite

            # Cache it
            self.sprite_cache[cache_key] = sprite

            return sprite.copy()

        except Exception as e:
            print(f"Error loading sprite {sprite_file}: {e}")
            return None

    # -------- 公共辅助：获取或重载 --------
    def reload(self, new_dir: str | Path | None = None) -> None:
        """Rescan sprite directory; optionally switch to a new directory."""
        if new_dir is not None:
            self.sprite_dir = Path(new_dir)
        else:
            # 如果当前目录没有 png，尝试重新挑选
            if not (self.sprite_dir.exists() and any(self.sprite_dir.glob("*.png"))):
                self.sprite_dir = self._pick_sprite_dir()

        self.sprite_cache.clear()
        self._scan_available_sprites()
        self.has_real_sprites = bool(self.sprite_mapping)
        if self.has_real_sprites:
            print(f"[sprite_loader] Reloaded. {len(self.sprite_mapping)} mappings from {self.sprite_dir}")
        else:
            print("[sprite_loader] Reloaded. No sprites found; using fallback.")

    def status(self) -> dict:
        """Return a small status dict for diagnostics."""
        try:
            png_count = len(list(self.sprite_dir.glob("*.png"))) if self.sprite_dir.exists() else 0
        except Exception:
            png_count = 0
        return {
            "sprite_dir": str(self.sprite_dir),
            "has_real_sprites": self.has_real_sprites,
            "mapped_names": len(self.sprite_mapping),
            "png_files": png_count,
            "env_BABA_SPRITES_DIR": os.getenv("BABA_SPRITES_DIR") or "",
        }

    def get_sprite_or_fallback(
        self,
        name: str,
        fallback_color: tuple[int, int, int],
        size: tuple[int, int] | None = None,
    ) -> np.ndarray:
        """
        Get a sprite or create a colored fallback.

        Args:
            name: Name of the sprite
            fallback_color: Color to use if sprite not found
            size: Target size

        Returns:
            Sprite or colored square
        """
        sprite = self.load_sprite(name, size)

        if sprite is not None:
            return sprite

        # Create fallback
        if size is None:
            size = self.default_size

        fallback = np.full((size[1], size[0], 3), fallback_color, dtype=np.uint8)

        # Add a border for visibility
        cv2.rectangle(
            fallback,
            (0, 0),
            (size[0] - 1, size[1] - 1),
            (
                max(0, fallback_color[0] - 50),
                max(0, fallback_color[1] - 50),
                max(0, fallback_color[2] - 50),
            ),
            1,
        )

        return fallback


# Global sprite loader instance
sprite_loader = SpriteLoader()
