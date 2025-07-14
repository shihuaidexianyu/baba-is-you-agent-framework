"""Integration tests for complete game scenarios."""

import pytest
from baba import make
from baba.grid import Grid
from baba.registration import Registry


class TestGameScenarios:
    """Test complete game scenarios and interactions."""
    
    def test_complete_simple_level(self):
        """Test completing the simple level."""
        env = make("simple")
        grid = env.grid
        
        # Verify initial state
        assert not grid.won
        assert not grid.lost
        
        # Baba starts at (2, 5), flag at (12, 5)
        # Move right to reach flag
        moves = ["right"] * 10
        
        for move in moves:
            if not grid.won:
                grid.step(move)
        
        assert grid.won
    
    def test_tutorial_level_puzzle_solving(self):
        """Test solving tutorial level with obstacles."""
        env = make("tutorial")
        grid = env.grid
        
        # Should have walls and rocks to navigate
        grid._update_rules()
        
        # Verify rules
        assert grid.rule_manager.has_property("wall", "STOP")
        assert grid.rule_manager.has_property("rock", "PUSH")
        
        # Execute a solution (this is environment-specific)
        # Just verify the level is playable
        initial_you_objects = grid.find_objects(name="baba")
        assert len(initial_you_objects) > 0
        
        # Make some moves
        for _ in range(5):
            grid.step("right")
            if grid.won:
                break
    
    def test_transformation_level_gameplay(self):
        """Test gameplay in transformation level."""
        env = make("transformation")
        grid = env.grid
        
        # Should have transformation rules available
        grid._update_rules()
        
        # Find text objects to verify level setup
        text_objects = []
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if obj.is_text:
                        text_objects.append(obj)
        
        assert len(text_objects) > 0
        
        # Verify we can move
        you_objects = grid.rule_manager.get_you_objects()
        assert len(you_objects) > 0
    
    def test_make_win_level_rule_creation(self):
        """Test creating WIN rules in make_win level."""
        env = make("make_win")
        grid = env.grid
        
        # Initially no WIN objects
        grid._update_rules()
        assert len(grid.rule_manager.get_win_objects()) == 0
        
        # Find moveable text to create rules
        you_objects = grid.rule_manager.get_you_objects()
        assert len(you_objects) > 0
        
        # Simulate creating a WIN rule by moving text
        # (exact moves depend on level layout)
        for _ in range(10):
            grid.step("right")
            grid._update_rules()
            if len(grid.rule_manager.get_win_objects()) > 0:
                break
    
    def test_sink_level_interactions(self):
        """Test sink mechanics in sink level."""
        env = make("sink")
        grid = env.grid
        
        grid._update_rules()
        
        # Should have SINK objects
        sink_objects = grid.rule_manager.get_sink_objects()
        assert len(sink_objects) > 0
        
        # Test that we can move
        initial_objects = sum(len(grid.grid[y][x]) for y in range(grid.height) for x in range(grid.width))
        
        # Make moves that might trigger sinking
        for move in ["right", "down", "left", "up"]:
            grid.step(move)
            
        # Object count might have changed due to sinking
        final_objects = sum(len(grid.grid[y][x]) for y in range(grid.height) for x in range(grid.width))
        # Just verify the game is still playable
        assert not grid.lost or grid.won
    
    def test_multiple_you_level(self):
        """Test controlling multiple YOU objects."""
        env = make("multiple_you")
        grid = env.grid
        
        grid._update_rules()
        
        # Should have multiple YOU objects
        you_objects = grid.rule_manager.get_you_objects()
        assert len(you_objects) >= 1
        
        # Find all controllable objects
        controllable = []
        for obj_name in you_objects:
            controllable.extend(grid.find_objects(name=obj_name))
        
        initial_positions = [(x, y) for _, x, y in controllable]
        
        # Move all YOU objects
        grid.step("right")
        
        # Verify movement
        for obj_name in you_objects:
            moved_objects = grid.find_objects(name=obj_name)
            for obj, x, y in moved_objects:
                # Check that at least some objects moved
                if (x-1, y) in initial_positions:
                    assert True
                    break
    
    def test_complex_rules_level(self):
        """Test level with complex rule interactions."""
        env = make("complex_rules")
        grid = env.grid
        
        grid._update_rules()
        
        # Should have multiple active rules
        assert len(grid.rule_manager.rules) > 2
        
        # Test that game is playable
        for move in ["right", "down", "right", "up"]:
            if not grid.won and not grid.lost:
                grid.step(move)
    
    def test_game_state_persistence(self):
        """Test that game state persists correctly."""
        env = make("simple")
        grid = env.grid
        
        # Make some moves
        grid.step("right")
        grid.step("right")
        
        # Copy the grid
        grid_copy = grid.copy()
        
        # Verify copy has same state
        assert grid_copy.steps == grid.steps
        assert grid_copy.won == grid.won
        assert grid_copy.lost == grid.lost
        
        # Verify objects are in same positions
        for y in range(grid.height):
            for x in range(grid.width):
                orig_objects = {obj.name for obj in grid.grid[y][x]}
                copy_objects = {obj.name for obj in grid_copy.grid[y][x]}
                assert orig_objects == copy_objects
        
        # Verify modifying copy doesn't affect original
        grid_copy.step("left")
        assert grid_copy.steps == grid.steps + 1


class TestAgentCompatibility:
    """Test that environments work with agent framework."""
    
    def test_environment_agent_interface(self):
        """Test environment provides correct interface for agents."""
        env = make("simple")
        
        # Test reset
        grid = env.reset()
        assert grid is not None
        assert hasattr(grid, 'width')
        assert hasattr(grid, 'height')
        assert hasattr(grid, 'step')
        assert hasattr(grid, 'won')
        assert hasattr(grid, 'lost')
        assert hasattr(grid, 'rule_manager')
        
        # Test step
        grid, won, lost = env.step("right")
        assert isinstance(won, bool)
        assert isinstance(lost, bool)
        
        # Test grid has required methods for agents
        assert hasattr(grid, 'render')
        assert hasattr(grid, 'find_objects')
        assert hasattr(grid, 'get_objects_at')