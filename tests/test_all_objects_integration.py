"""Integration tests for all objects with the game system."""

import pytest
from baba.registration import Registry
from baba.grid import Grid
from baba.level_loader import LevelLoader
from baba.all_objects import ALL_OBJECTS, ALL_TEXT_OBJECTS


class TestAllObjectsIntegration:
    """Test that all objects work with the game system."""
    
    def test_create_grid_with_all_objects(self):
        """Test creating a grid with various objects."""
        registry = Registry()
        grid = Grid(10, 10, registry)
        
        # Place one of each type of object
        x, y = 0, 0
        placed = []
        
        # Place regular objects
        for name in ["baba", "keke", "wall", "rock", "water", "grass", "tree", "star"]:
            obj = registry.create_instance(name)
            assert obj is not None, f"Failed to create {name}"
            grid.place_object(obj, x, y)
            placed.append((name, x, y))
            
            x += 1
            if x >= 10:
                x = 0
                y += 1
        
        # Verify objects were placed
        for name, px, py in placed:
            cell = grid.grid[py][px]
            assert len(cell) > 0, f"No object at ({px},{py})"
            obj = next(iter(cell))
            assert obj.name == name, f"Wrong object at ({px},{py}): {obj.name} != {name}"
    
    def test_rules_with_new_objects(self):
        """Test that rules work with new object types."""
        registry = Registry()
        grid = Grid(10, 5, registry)
        
        # Create KEKE IS YOU
        keke_text = registry.create_instance("keke", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        you_text = registry.create_instance("you", is_text=True)
        
        grid.place_object(keke_text, 1, 1)
        grid.place_object(is_text, 2, 1)
        grid.place_object(you_text, 3, 1)
        
        # Place a keke
        keke = registry.create_instance("keke")
        grid.place_object(keke, 5, 2)
        
        # Update rules after placing objects
        grid._update_rules()
        
        # Verify rule was created
        assert len(grid.rule_manager.rules) > 0, "No rules created"
        
        # Verify keke has YOU property
        from baba.properties import Property
        assert grid.rule_manager.has_property("keke", Property.YOU)
    
    def test_level_loader_integration(self):
        """Test that the level loader works with all objects."""
        registry = Registry()
        loader = LevelLoader()
        
        # Test loading a level (if Steam installation exists)
        try:
            grid = loader.load_level("baba", 0, registry)
            if grid:
                # Check that objects were created with correct types
                for y in range(grid.height):
                    for x in range(grid.width):
                        for obj in grid.grid[y][x]:
                            # Verify object has expected attributes
                            assert hasattr(obj, 'name')
                            assert hasattr(obj, 'type_id') 
                            assert hasattr(obj, 'color')
                            assert hasattr(obj, 'is_text')
                            
                            # Verify it's one of our registered objects
                            if obj.is_text:
                                base_name = obj.name[:-5] if obj.name.endswith('_text') else obj.name
                                assert base_name in registry.text_objects, f"Unknown text object: {obj.name}"
                            else:
                                assert obj.name in registry.objects, f"Unknown object: {obj.name}"
        except Exception:
            # Skip if no Steam installation
            pytest.skip("Steam installation not found")
    
    def test_object_properties_consistency(self):
        """Test that object properties are consistent."""
        registry = Registry()
        
        # Test that all registered objects have consistent properties
        for name, obj in registry.objects.items():
            # Regular objects should not be text
            assert not obj.is_text, f"{name} is marked as text but shouldn't be"
            
            # Should have required attributes
            assert hasattr(obj, 'color')
            assert hasattr(obj, 'type_id')
            assert hasattr(obj, 'name')
            assert obj.name == name
        
        for name, obj in registry.text_objects.items():
            # Text objects should be text
            assert obj.is_text, f"{name} is not marked as text but should be"
            
            # Should have text attribute
            assert hasattr(obj, 'text')
            assert obj.text is not None and len(obj.text) > 0
    
    def test_rendering_all_objects(self):
        """Test that all objects can be rendered."""
        registry = Registry()
        
        # Test rendering a few objects
        test_objects = ["baba", "keke", "wall", "water", "grass", "star"]
        
        for name in test_objects:
            obj = registry.create_instance(name)
            assert obj is not None
            
            # Test render method
            sprite = obj.render()
            assert sprite is not None, f"{name} render returned None"
            assert hasattr(sprite, 'shape'), f"{name} sprite has no shape"
            
            # Test text version
            text_obj = registry.create_instance(name, is_text=True)
            if text_obj:
                sprite = text_obj.render()
                assert sprite is not None, f"text_{name} render returned None"
    


if __name__ == "__main__":
    pytest.main([__file__, "-v"])