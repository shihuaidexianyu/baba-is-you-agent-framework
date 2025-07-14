"""Test suite for Grid functionality."""

import pytest
from baba.grid import Grid
from baba.registration import Registry
from baba.properties import Property


class TestGridBasics:
    """Test basic grid operations."""
    
    @pytest.fixture
    def grid_setup(self):
        """Set up a basic grid for testing."""
        registry = Registry()
        grid = Grid(10, 10, registry)
        return grid, registry
    
    def test_grid_initialization(self, grid_setup):
        """Test grid is properly initialized."""
        grid, registry = grid_setup
        assert grid.width == 10
        assert grid.height == 10
        assert len(grid.grid) == 10
        assert all(len(row) == 10 for row in grid.grid)
        assert all(isinstance(cell, set) for row in grid.grid for cell in row)
    
    def test_place_object(self, grid_setup):
        """Test placing objects on the grid."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        
        grid.place_object(baba, 5, 5)
        assert baba in grid.grid[5][5]
        assert len(grid.get_objects_at(5, 5)) == 1
    
    def test_remove_object(self, grid_setup):
        """Test removing objects from the grid."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        
        grid.place_object(baba, 5, 5)
        grid.remove_object(baba, 5, 5)
        assert baba not in grid.grid[5][5]
        assert len(grid.get_objects_at(5, 5)) == 0
    
    def test_out_of_bounds_operations(self, grid_setup):
        """Test operations outside grid bounds."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        
        # Place out of bounds - should fail silently
        grid.place_object(baba, 15, 15)
        grid.place_object(baba, -1, -1)
        
        # Get objects out of bounds - should return empty set
        assert len(grid.get_objects_at(15, 15)) == 0
        assert len(grid.get_objects_at(-1, -1)) == 0
    
    def test_multiple_objects_at_position(self, grid_setup):
        """Test multiple objects can occupy the same position."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        rock = registry.create_instance("rock")
        
        grid.place_object(baba, 5, 5)
        grid.place_object(rock, 5, 5)
        
        objects = grid.get_objects_at(5, 5)
        assert len(objects) == 2
        assert baba in objects
        assert rock in objects
    
    def test_move_object(self, grid_setup):
        """Test moving objects on the grid."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        
        grid.place_object(baba, 5, 5)
        success = grid.move_object(baba, 5, 5, 6, 5)
        
        assert success
        assert baba not in grid.get_objects_at(5, 5)
        assert baba in grid.get_objects_at(6, 5)
    
    def test_move_object_out_of_bounds(self, grid_setup):
        """Test moving objects out of bounds fails."""
        grid, registry = grid_setup
        baba = registry.create_instance("baba")
        
        grid.place_object(baba, 5, 5)
        success = grid.move_object(baba, 5, 5, 15, 15)
        
        assert not success
        assert baba in grid.get_objects_at(5, 5)
    
    def test_find_objects_by_name(self, grid_setup):
        """Test finding objects by name."""
        grid, registry = grid_setup
        baba1 = registry.create_instance("baba")
        baba2 = registry.create_instance("baba")
        rock = registry.create_instance("rock")
        
        grid.place_object(baba1, 1, 1)
        grid.place_object(baba2, 2, 2)
        grid.place_object(rock, 3, 3)
        
        babas = grid.find_objects(name="baba")
        assert len(babas) == 2
        assert all(obj.name == "baba" for obj, _, _ in babas)
        
        rocks = grid.find_objects(name="rock")
        assert len(rocks) == 1
        assert rocks[0][0].name == "rock"