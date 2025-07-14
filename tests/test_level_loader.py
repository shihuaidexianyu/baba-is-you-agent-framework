"""Test suite for level loader functionality."""

import pytest
from pathlib import Path
from baba.level_loader import LevelLoader
from baba.registration import Registry


class TestLevelLoader:
    """Test the level loading system."""
    
    @pytest.fixture
    def loader(self):
        """Create a level loader instance."""
        return LevelLoader()
    
    @pytest.fixture
    def registry(self):
        """Create a registry instance."""
        return Registry()
    
    def test_level_loader_initialization(self, loader):
        """Test level loader initializes correctly."""
        assert loader.game_path is not None
        assert loader.data_path is not None
        assert loader.worlds_path is not None
    
    def test_has_steam_levels(self, loader):
        """Test detecting if Steam levels are available."""
        has_levels = loader.has_steam_levels()
        assert isinstance(has_levels, bool)
    
    @pytest.mark.skipif(not LevelLoader().has_steam_levels(), reason="Steam levels not available")
    def test_load_basic_level(self, loader, registry):
        """Test loading a basic level from world 'baba'."""
        grid = loader.load_level("baba", 0, registry)
        
        assert grid is not None, "Failed to load level"
        assert grid.width > 0 and grid.height > 0, "Invalid grid dimensions"
        
        # Count objects
        total_objects = 0
        object_counts = {}
        for y in range(grid.height):
            for x in range(grid.width):
                objs = grid.grid[y][x]
                total_objects += len(objs)
                for obj in objs:
                    obj_name = obj.name
                    object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
        
        assert total_objects > 0, "No objects loaded"
        assert len(object_counts) > 0, "No object types found"
        
        # Verify objects have required attributes
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    assert hasattr(obj, 'name')
                    assert hasattr(obj, 'type_id')
                    assert hasattr(obj, 'color')
                    assert hasattr(obj, 'is_text')
    
    
    @pytest.mark.skipif(not LevelLoader().has_steam_levels(), reason="Steam levels not available")
    def test_load_multiple_levels(self, loader, registry):
        """Test loading multiple levels to ensure consistency."""
        levels_to_test = [
            ("baba", 0),
            ("baba", 1),
            ("baba", 2)
        ]
        
        for world, level_num in levels_to_test:
            grid = loader.load_level(world, level_num, registry)
            if grid:  # Some levels might not exist
                assert grid.width > 0 and grid.height > 0
                
                # Every level should have at least some objects
                total_objects = sum(len(grid.grid[y][x]) for y in range(grid.height) for x in range(grid.width))
                assert total_objects > 0, f"No objects in {world} level {level_num}"
    
    def test_object_id_mapping(self, loader):
        """Test that object IDs map correctly to names."""
        from baba.object_ids import get_object_name
        
        # Test some known mappings
        assert get_object_name(1) == "baba"  # ID 1 is baba
        assert get_object_name(5) == "wall"  # ID 5 is wall
        assert get_object_name(6) == "rock"  # ID 6 is rock
        assert get_object_name(7) == "flag"  # ID 7 is flag
        
        # Test text object mappings
        assert get_object_name(90) == "text_you"  # ID 90 is text_you
        assert get_object_name(91) == "text_win"  # ID 91 is text_win
        assert get_object_name(92) == "text_stop"  # ID 92 is text_stop