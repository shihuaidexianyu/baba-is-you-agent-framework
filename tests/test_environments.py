"""Test suite for level loading and environments."""

import pytest
from baba import make
from baba.level_loader import LevelLoader
from baba.registration import Registry
import os
import tempfile
import json


class TestEnvironments:
    """Test all pre-built environments."""
    
    def test_all_environments_load(self):
        """Test that all environments can be created without errors."""
        environments = [
            "tutorial", "simple", "make_win", "push_puzzle",
            "transformation", "multiple_you", "complex_rules",
            "sink", "maze", "key_door", "teleport", 
            "conditional", "recursive_rules", "empty"
        ]
        
        for env_name in environments:
            env = make(env_name)
            assert env is not None
            assert env.grid is not None
            assert env.grid.width > 0
            assert env.grid.height > 0
    
    def test_tutorial_environment_setup(self):
        """Test tutorial environment has correct setup."""
        env = make("tutorial")
        grid = env.grid
        
        # Check that rules are present
        grid._update_rules()
        assert grid.rule_manager.has_property("baba", "YOU")
        assert grid.rule_manager.has_property("flag", "WIN")
        assert grid.rule_manager.has_property("wall", "STOP")
        assert grid.rule_manager.has_property("rock", "PUSH")
        
        # Check that objects exist
        babas = grid.find_objects(name="baba")
        flags = grid.find_objects(name="flag")
        assert len(babas) > 0
        assert len(flags) > 0
    
    def test_make_win_environment_specific(self):
        """Test make_win environment allows creating win conditions."""
        env = make("make_win")
        grid = env.grid
        
        # Should start with BABA IS YOU but no WIN condition
        grid._update_rules()
        assert grid.rule_manager.has_property("baba", "YOU")
        assert len(grid.rule_manager.get_win_objects()) == 0
        
        # Check text objects are present for making rules
        text_objects = []
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if obj.is_text:
                        text_objects.append(obj)
        
        assert len(text_objects) > 0
    
    def test_sink_environment_has_sink_objects(self):
        """Test sink environment has SINK mechanics."""
        env = make("sink")
        grid = env.grid
        
        grid._update_rules()
        sink_objects = grid.rule_manager.get_sink_objects()
        assert len(sink_objects) > 0
    
    def test_empty_environment_is_empty(self):
        """Test empty environment starts with no objects."""
        env = make("empty")
        grid = env.grid
        
        # Check grid is truly empty
        object_count = 0
        for y in range(grid.height):
            for x in range(grid.width):
                object_count += len(grid.grid[y][x])
        
        assert object_count == 0
    
    def test_environment_reset(self):
        """Test that environments can be reset."""
        env = make("simple")
        grid = env.grid
        
        # Make some changes
        grid.step("right")
        grid.step("down")
        
        # Reset
        new_grid = env.reset()
        
        # Should be a fresh grid
        assert new_grid != grid
        assert new_grid.steps == 0
        assert not new_grid.won
        assert not new_grid.lost


class TestLevelLoader:
    """Test the level loading system."""
    
    @pytest.fixture
    def loader_setup(self):
        """Set up level loader with registry."""
        registry = Registry()
        loader = LevelLoader(registry)
        return loader, registry
    
    def test_load_simple_level(self, loader_setup):
        """Test loading a simple level format."""
        loader, registry = loader_setup
        
        level_data = {
            "width": 5,
            "height": 5,
            "objects": [
                {"type": "baba", "x": 1, "y": 1},
                {"type": "flag", "x": 3, "y": 3},
                {"type": "text_baba", "x": 0, "y": 0},
                {"type": "text_is", "x": 1, "y": 0},
                {"type": "text_you", "x": 2, "y": 0}
            ]
        }
        
        grid = loader.load_from_dict(level_data)
        
        assert grid.width == 5
        assert grid.height == 5
        
        # Check objects were placed
        assert len(grid.get_objects_at(1, 1)) == 1
        assert len(grid.get_objects_at(3, 3)) == 1
        
        # Check text objects
        text_obj = list(grid.get_objects_at(0, 0))[0]
        assert text_obj.is_text
    
    def test_load_level_with_invalid_positions(self, loader_setup):
        """Test loading handles invalid positions gracefully."""
        loader, registry = loader_setup
        
        level_data = {
            "width": 5,
            "height": 5,
            "objects": [
                {"type": "baba", "x": 1, "y": 1},
                {"type": "flag", "x": 10, "y": 10},  # Out of bounds
                {"type": "rock", "x": -1, "y": -1}   # Negative
            ]
        }
        
        grid = loader.load_from_dict(level_data)
        
        # Only the valid object should be placed
        object_count = sum(len(grid.grid[y][x]) for y in range(5) for x in range(5))
        assert object_count == 1
    
    def test_load_from_file(self, loader_setup):
        """Test loading level from JSON file."""
        loader, registry = loader_setup
        
        level_data = {
            "width": 8,
            "height": 6,
            "objects": [
                {"type": "baba", "x": 2, "y": 3},
                {"type": "rock", "x": 4, "y": 3},
                {"type": "text_rock", "x": 1, "y": 1},
                {"type": "text_is", "x": 2, "y": 1},
                {"type": "text_push", "x": 3, "y": 1}
            ]
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(level_data, f)
            temp_path = f.name
        
        try:
            grid = loader.load_from_file(temp_path)
            
            assert grid.width == 8
            assert grid.height == 6
            
            # Check specific objects
            babas = grid.find_objects(name="baba")
            assert len(babas) == 1
            assert babas[0][1] == 2  # x position
            assert babas[0][2] == 3  # y position
            
        finally:
            os.unlink(temp_path)
    
    def test_load_with_text_objects(self, loader_setup):
        """Test that text objects are created with proper types."""
        loader, registry = loader_setup
        
        level_data = {
            "width": 10,
            "height": 10,
            "objects": [
                {"type": "text_baba", "x": 1, "y": 1},
                {"type": "text_rock", "x": 2, "y": 1},
                {"type": "text_win", "x": 3, "y": 1}
            ]
        }
        
        grid = loader.load_from_dict(level_data)
        
        # Check text objects have correct properties
        for x in range(1, 4):
            obj = list(grid.get_objects_at(x, 1))[0]
            assert obj.is_text
            assert hasattr(obj, 'text')
            
            # Check specific text object types
            if x == 1:
                assert obj.name == "baba"
                assert hasattr(obj, 'noun')
            elif x == 3:
                assert obj.name == "win"
                assert hasattr(obj, 'property')
    
    def test_save_and_load_level(self, loader_setup):
        """Test saving a level and loading it back."""
        loader, registry = loader_setup
        
        # Create a level
        original_data = {
            "width": 7,
            "height": 7,
            "objects": [
                {"type": "baba", "x": 3, "y": 3},
                {"type": "wall", "x": 2, "y": 2},
                {"type": "wall", "x": 3, "y": 2},
                {"type": "wall", "x": 4, "y": 2},
                {"type": "text_baba", "x": 1, "y": 6},
                {"type": "text_is", "x": 2, "y": 6},
                {"type": "text_you", "x": 3, "y": 6}
            ]
        }
        
        # Load original
        grid = loader.load_from_dict(original_data)
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            loader.save_to_file(grid, temp_path)
            
            # Load it back
            loaded_grid = loader.load_from_file(temp_path)
            
            # Verify dimensions
            assert loaded_grid.width == grid.width
            assert loaded_grid.height == grid.height
            
            # Verify object counts match
            original_count = sum(len(grid.grid[y][x]) for y in range(7) for x in range(7))
            loaded_count = sum(len(loaded_grid.grid[y][x]) for y in range(7) for x in range(7))
            assert loaded_count == original_count
            
        finally:
            os.unlink(temp_path)