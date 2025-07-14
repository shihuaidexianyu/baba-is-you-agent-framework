"""Test suite for all Baba Is You objects."""

import pytest

from baba.all_objects import (
    ALL_OBJECTS,
    ALL_TEXT_OBJECTS,
    # Test a few specific objects
    BabaObject,
    BabaTextObject,
    IsTextObject,
    KekeObject,
    WallObject,
    YouTextObject,
)
from baba.object_ids import ID_TO_NAME
from baba.properties import Property


class TestAllObjects:
    """Test all game objects are properly defined."""

    def test_all_objects_count(self):
        """Test we have the expected number of objects."""
        # Based on the object_ids.py file, we should have specific counts
        assert len(ALL_OBJECTS) == 44  # Regular objects
        assert len(ALL_TEXT_OBJECTS) == 66  # Text objects (including properties and verbs)

    def test_object_ids_match(self):
        """Test that object IDs match the ID_TO_NAME mapping."""
        # Test regular objects
        for name, obj_class in ALL_OBJECTS.items():
            obj = obj_class()
            assert obj.name == name, f"Object name mismatch for {name}"

            # Check ID exists in mapping
            if hasattr(obj, "type_id"):
                assert obj.type_id in ID_TO_NAME, f"ID {obj.type_id} not in ID_TO_NAME"
                # For most objects, the name should match (except special cases)
                expected_name = ID_TO_NAME[obj.type_id]
                if expected_name not in ["empty", "cursor"] and not expected_name.startswith(
                    "default"
                ):
                    assert (
                        obj.name == expected_name
                    ), f"Name mismatch: {obj.name} != {expected_name}"

    def test_text_objects_have_correct_structure(self):
        """Test text objects have proper attributes."""
        for name, text_class in ALL_TEXT_OBJECTS.items():
            obj = text_class()

            # All text objects should be marked as text
            assert obj.is_text, f"{name} is not marked as text"

            # Should have text attribute
            assert hasattr(obj, "text"), f"{name} missing text attribute"

            # Check specific types
            if hasattr(obj, "noun") and obj.noun is not None:
                # Noun text objects
                assert obj.text == obj.noun.upper(), f"{name} text doesn't match noun"
                assert name == f"text_{obj.noun}", f"{name} name format incorrect"
            elif hasattr(obj, "property") and obj.property is not None:
                # Property text objects
                assert isinstance(obj.property, Property), f"{name} property not a Property enum"
                assert obj.text == obj.property.name, f"{name} text doesn't match property"
            elif hasattr(obj, "verb") and obj.verb is not None:
                # Verb text objects
                assert obj.text == obj.verb.upper(), f"{name} text doesn't match verb"
            elif hasattr(obj, "special") and obj.special is not None:
                # Special text objects
                assert obj.text == obj.special.upper(), f"{name} text doesn't match special"

    def test_all_objects_have_required_attributes(self):
        """Test all objects have required attributes."""
        all_objs = list(ALL_OBJECTS.items()) + list(ALL_TEXT_OBJECTS.items())

        for name, obj_class in all_objs:
            obj = obj_class()

            # Required attributes
            assert hasattr(obj, "name"), f"{name} missing name"
            assert hasattr(obj, "type_id"), f"{name} missing type_id"
            assert hasattr(obj, "color"), f"{name} missing color"
            assert hasattr(obj, "is_text"), f"{name} missing is_text"

            # Check color format
            assert isinstance(obj.color, tuple), f"{name} color not a tuple"
            assert len(obj.color) == 3, f"{name} color not RGB"
            assert all(0 <= c <= 255 for c in obj.color), f"{name} color out of range"

            # Regular objects should have char
            if not obj.is_text:
                assert hasattr(obj, "char"), f"{name} missing char attribute"

    def test_specific_objects(self):
        """Test specific important objects."""
        # Test Baba
        baba = BabaObject()
        assert baba.name == "baba"
        assert baba.type_id == 1
        assert baba.char == "B"
        assert not baba.is_text

        # Test Keke
        keke = KekeObject()
        assert keke.name == "keke"
        assert keke.type_id == 2
        assert keke.char == "K"

        # Test Wall
        wall = WallObject()
        assert wall.name == "wall"
        assert wall.type_id == 5
        assert not wall.traversible
        assert not wall.displaceable

    def test_text_object_properties(self):
        """Test text objects with properties."""
        # Test YOU
        you = YouTextObject()
        assert you.property == Property.YOU
        assert you.text == "YOU"
        assert you.is_text

        # Test IS
        is_text = IsTextObject()
        assert is_text.verb == "is"
        assert is_text.text == "IS"

        # Test BABA text
        baba_text = BabaTextObject()
        assert baba_text.noun == "baba"
        assert baba_text.text == "BABA"

    def test_unique_type_ids(self):
        """Test that all type IDs are unique."""
        seen_ids = {}

        # Check regular objects
        for name, obj_class in ALL_OBJECTS.items():
            obj = obj_class()
            if obj.type_id in seen_ids:
                pytest.fail(
                    f"Duplicate type_id {obj.type_id} in {name} and {seen_ids[obj.type_id]}"
                )
            seen_ids[obj.type_id] = name

        # Check text objects
        for name, obj_class in ALL_TEXT_OBJECTS.items():
            obj = obj_class()
            if obj.type_id in seen_ids:
                pytest.fail(
                    f"Duplicate type_id {obj.type_id} in {name} and {seen_ids[obj.type_id]}"
                )
            seen_ids[obj.type_id] = name

    def test_object_categories(self):
        """Test objects by category."""
        # Characters
        characters = ["baba", "keke", "anni", "me"]
        for char in characters:
            assert char in ALL_OBJECTS, f"Missing character: {char}"
            assert f"text_{char}" in ALL_TEXT_OBJECTS, f"Missing text for: {char}"

        # Structures
        structures = ["wall", "rock", "flag", "tile", "grass", "brick", "hedge"]
        for struct in structures:
            assert struct in ALL_OBJECTS, f"Missing structure: {struct}"
            assert f"text_{struct}" in ALL_TEXT_OBJECTS, f"Missing text for: {struct}"

        # Liquids
        liquids = ["water", "lava", "bog"]
        for liquid in liquids:
            assert liquid in ALL_OBJECTS, f"Missing liquid: {liquid}"
            assert f"text_{liquid}" in ALL_TEXT_OBJECTS, f"Missing text for: {liquid}"

    def test_property_text_objects(self):
        """Test all properties have corresponding text objects."""
        property_names = [
            "you",
            "win",
            "stop",
            "push",
            "sink",
            "defeat",
            "hot",
            "melt",
            "move",
            "float",
            "shift",
            "tele",
            "pull",
            "open",
            "shut",
            "weak",
        ]

        for prop in property_names:
            text_name = f"text_{prop}"
            assert text_name in ALL_TEXT_OBJECTS, f"Missing property text: {text_name}"

            # Check it has the right property
            obj = ALL_TEXT_OBJECTS[text_name]()
            assert hasattr(obj, "property"), f"{text_name} missing property attribute"
            assert obj.property.name.lower() == prop, f"{text_name} property mismatch"

    def test_verb_text_objects(self):
        """Test verb text objects."""
        verbs = ["is", "and", "not"]

        for verb in verbs:
            text_name = f"text_{verb}"
            assert text_name in ALL_TEXT_OBJECTS, f"Missing verb text: {text_name}"

            obj = ALL_TEXT_OBJECTS[text_name]()
            assert hasattr(obj, "verb"), f"{text_name} missing verb attribute"
            assert obj.verb == verb, f"{text_name} verb mismatch"


class TestObjectBehavior:
    """Test object behavior and methods."""

    def test_object_equality(self):
        """Test object equality and hashing."""
        baba1 = BabaObject()
        baba2 = BabaObject()
        keke = KekeObject()

        # Objects with same type_id should hash the same
        assert hash(baba1) == hash(baba2)

        # Different objects should have different hashes
        assert hash(baba1) != hash(keke)

        # Test string equality
        assert baba1 == "baba"
        assert baba1 != "keke"

    def test_object_repr(self):
        """Test object string representation."""
        baba = BabaObject()
        repr_str = repr(baba)
        assert "baba" in repr_str or "BabaObject" in repr_str
        assert str(baba.type_id) in repr_str or "type_id=1" in repr_str

        baba_text = BabaTextObject()
        repr_str = repr(baba_text)
        assert "text_baba" in repr_str or "BabaTextObject" in repr_str

    def test_render_method(self):
        """Test objects have render method."""
        # Test a few objects
        for obj_class in [BabaObject, WallObject, BabaTextObject]:
            obj = obj_class()
            assert hasattr(obj, "render"), f"{obj.name} missing render method"

            # Should be able to call render
            sprite = obj.render()
            assert sprite is not None, f"{obj.name} render returned None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
