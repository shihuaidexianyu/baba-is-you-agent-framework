"""Test suite for game objects and registration."""

import pytest
from baba.registration import Registry
from baba.world_object import Object, TextObject
from baba.properties import Property


class TestRegistry:
    """Test the object registry system."""
    
    def test_registry_initialization(self):
        """Test registry initializes with all object types."""
        registry = Registry()
        
        # Check some core objects exist
        assert "baba" in registry.objects
        assert "rock" in registry.objects
        assert "flag" in registry.objects
        assert "wall" in registry.objects
        
        # Check text objects exist
        assert "baba" in registry.text_objects
        assert "is" in registry.text_objects
        assert "you" in registry.text_objects
    
    def test_create_regular_object(self):
        """Test creating regular game objects."""
        registry = Registry()
        
        baba = registry.create_instance("baba")
        assert baba is not None
        assert baba.name == "baba"
        assert not baba.is_text
        assert hasattr(baba, 'color')
    
    def test_create_text_object(self):
        """Test creating text objects."""
        registry = Registry()
        
        baba_text = registry.create_instance("baba", is_text=True)
        assert baba_text is not None
        assert baba_text.name == "baba_text"  # Text objects have _text suffix
        assert baba_text.is_text
        assert hasattr(baba_text, 'text')
        assert baba_text.text == "BABA"
    
    def test_create_property_text(self):
        """Test creating property text objects."""
        registry = Registry()
        
        you_text = registry.create_instance("you", is_text=True)
        assert you_text is not None
        assert you_text.is_text
        assert hasattr(you_text, 'property')
        assert you_text.property == Property.YOU
    
    def test_create_invalid_object(self):
        """Test creating non-existent objects returns None."""
        registry = Registry()
        
        obj = registry.create_instance("nonexistent")
        assert obj is None
        
        obj = registry.create_instance("nonexistent", is_text=True)
        assert obj is None
    
    def test_get_object(self):
        """Test getting object templates."""
        registry = Registry()
        
        baba_template = registry.get_object("baba")
        assert baba_template is not None
        assert baba_template.name == "baba"
        
        # Should be the template, not an instance
        baba_instance = registry.create_instance("baba")
        assert baba_template is not baba_instance
    
    def test_object_independence(self):
        """Test that created objects are independent."""
        registry = Registry()
        
        baba1 = registry.create_instance("baba")
        baba2 = registry.create_instance("baba")
        
        assert baba1 is not baba2
        assert id(baba1) != id(baba2)


class TestWorldObjects:
    """Test world object properties and behavior."""
    
    def test_object_attributes(self):
        """Test basic object attributes."""
        registry = Registry()
        
        baba = registry.create_instance("baba")
        assert hasattr(baba, 'name')
        assert hasattr(baba, 'type_id')
        assert hasattr(baba, 'is_text')
        assert hasattr(baba, 'color')
        assert hasattr(baba, 'char')
    
    def test_text_object_attributes(self):
        """Test text object specific attributes."""
        registry = Registry()
        
        baba_text = registry.create_instance("baba", is_text=True)
        assert hasattr(baba_text, 'text')
        assert hasattr(baba_text, 'noun')
        assert baba_text.noun == "baba"
        
        you_text = registry.create_instance("you", is_text=True)
        assert hasattr(you_text, 'property')
        assert hasattr(you_text, 'noun')  # Has noun attr but it's None
        assert you_text.noun is None
    
    def test_object_equality(self):
        """Test object equality and hashing."""
        registry = Registry()
        
        baba1 = registry.create_instance("baba")
        baba2 = registry.create_instance("baba")
        rock = registry.create_instance("rock")
        
        # Objects with same attributes are equal
        assert baba1 == baba2  # Same type and attributes
        assert id(baba1) != id(baba2)  # But different instances
        
        # Different types should not be equal
        assert baba1 != rock
        
        # Objects should be hashable but equal objects hash the same
        obj_set = {baba1, baba2, rock}
        assert len(obj_set) == 2  # baba1 and baba2 are equal, so only 2 unique
    
    def test_all_objects_have_required_fields(self):
        """Test all registered objects have required fields."""
        registry = Registry()
        
        # Test regular objects
        for name, obj_class in registry.objects.items():
            obj = registry.create_instance(name)
            assert obj is not None, f"Failed to create {name}"
            assert hasattr(obj, 'name'), f"{name} missing 'name'"
            assert hasattr(obj, 'type_id'), f"{name} missing 'type_id'"
            assert hasattr(obj, 'is_text'), f"{name} missing 'is_text'"
            assert hasattr(obj, 'color'), f"{name} missing 'color'"
            assert obj.name == name, f"{name} has wrong name: {obj.name}"
        
        # Test text objects
        for name, text_class in registry.text_objects.items():
            text_obj = registry.create_instance(name, is_text=True)
            if text_obj is not None:  # Some objects might not have text versions
                assert text_obj.is_text
                assert hasattr(text_obj, 'text')
    
    def test_color_format(self):
        """Test that colors are in correct format."""
        registry = Registry()
        
        for name in registry.objects:
            obj = registry.create_instance(name)
            if obj:
                assert isinstance(obj.color, tuple), f"{name} color not a tuple"
                assert len(obj.color) == 3, f"{name} color not RGB"
                assert all(0 <= c <= 255 for c in obj.color), f"{name} color values out of range"