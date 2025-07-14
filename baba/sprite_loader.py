"""Load and manage actual Baba Is You sprites."""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import cv2
from PIL import Image


class SpriteLoader:
    """Loads and caches actual game sprites with fallback support."""
    
    def __init__(self):
        self.sprite_dir = Path(__file__).parent / "assets" / "sprites"
        self.sprite_cache: Dict[str, np.ndarray] = {}
        self.default_size = (24, 24)
        self.has_real_sprites = False
        
        # We'll dynamically find sprites based on naming pattern
        self.sprite_mapping = {}
        self._scan_available_sprites()
        
        # Check if we have real sprites
        png_files = list(self.sprite_dir.glob("*.png"))
        if len(png_files) > 10:  # Arbitrary threshold
            self.has_real_sprites = True
            print(f"Found {len(png_files)} Baba Is You sprites!")
        else:
            print("No game sprites found. Using custom fallback sprites.")
    
    def _scan_available_sprites(self):
        """Scan the sprite directory and build mapping."""
        if not self.sprite_dir.exists():
            return
            
        # Find all sprite files
        for sprite_file in self.sprite_dir.glob("*.png"):
            name_parts = sprite_file.stem.split("_")
            
            if len(name_parts) >= 3:
                # Format is typically: object_variant_frame.png
                # For now, we'll use the default variant 0, frame 1
                if name_parts[-2] == "0" and name_parts[-1] == "1":
                    base_name = "_".join(name_parts[:-2])
                    self.sprite_mapping[base_name] = sprite_file.name
                    
                    # Add alternative mappings for text objects
                    if base_name.startswith("text_"):
                        alt_name = base_name[5:] + "_text"
                        self.sprite_mapping[alt_name] = sprite_file.name
    
    def load_sprite(self, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[np.ndarray]:
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
        
        # Get sprite filename
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
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
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
    
    def get_sprite_or_fallback(self, name: str, fallback_color: Tuple[int, int, int], 
                              size: Optional[Tuple[int, int]] = None) -> np.ndarray:
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
        cv2.rectangle(fallback, (0, 0), (size[0]-1, size[1]-1), 
                     (max(0, fallback_color[0]-50), 
                      max(0, fallback_color[1]-50), 
                      max(0, fallback_color[2]-50)), 1)
        
        return fallback


# Global sprite loader instance
sprite_loader = SpriteLoader()