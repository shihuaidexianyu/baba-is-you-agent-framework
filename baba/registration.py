"""Object registry system for Baba Is You."""

from typing import Dict, List, Optional, Type

from .world_object import Object
from .all_objects import ALL_OBJECTS, ALL_TEXT_OBJECTS


class Registry:
    """Registry for all game objects."""

    def __init__(self):
        """Initialize the registry."""
        self.objects: Dict[str, Object] = {}
        self.text_objects: Dict[str, Object] = {}
        self.type_id_counter = 0
        
        # Register default objects
        self._register_defaults()

    def _register_defaults(self):
        """Register all default game objects."""
        # Register all game objects
        for name, obj_class in ALL_OBJECTS.items():
            self.register_object(name, obj_class)
        
        # Register all text objects
        for name, text_class in ALL_TEXT_OBJECTS.items():
            # Extract the base name (remove 'text_' prefix)
            base_name = name[5:] if name.startswith('text_') else name
            self.register_text_object(base_name, text_class)

    def register_object(self, name: str, obj_class: Type[Object]):
        """
        Register a game object.

        Args:
            name: Name of the object
            obj_class: Class of the object
        """
        obj = obj_class()
        obj.name = name
        obj.type_id = self._get_next_type_id()
        self.objects[name.lower()] = obj

    def register_text_object(self, name: str, obj_class: Type[Object]):
        """
        Register a text object.

        Args:
            name: Name of the text object
            obj_class: Class of the text object
        """
        obj = obj_class()
        obj.name = name + "_text"
        obj.type_id = self._get_next_type_id()
        self.text_objects[name.lower()] = obj

    def _get_next_type_id(self) -> int:
        """Get the next available type ID."""
        self.type_id_counter += 1
        return self.type_id_counter

    def get_object(self, name: str) -> Optional[Object]:
        """
        Get a game object by name.

        Args:
            name: Name of the object

        Returns:
            The object if found, None otherwise
        """
        return self.objects.get(name.lower())

    def get_text_object(self, name: str) -> Optional[Object]:
        """
        Get a text object by name.

        Args:
            name: Name of the text object

        Returns:
            The text object if found, None otherwise
        """
        return self.text_objects.get(name.lower())

    def get_all_objects(self) -> List[Object]:
        """Get all registered game objects."""
        return list(self.objects.values())

    def get_all_text_objects(self) -> List[Object]:
        """Get all registered text objects."""
        return list(self.text_objects.values())

    def get_object_by_type_id(self, type_id: int) -> Optional[Object]:
        """
        Get an object by its type ID.

        Args:
            type_id: Type ID of the object

        Returns:
            The object if found, None otherwise
        """
        # Search in game objects
        for obj in self.objects.values():
            if obj.type_id == type_id:
                return obj
        
        # Search in text objects
        for obj in self.text_objects.values():
            if obj.type_id == type_id:
                return obj
        
        return None

    def create_instance(self, name: str, is_text: bool = False) -> Optional[Object]:
        """
        Create a new instance of an object.

        Args:
            name: Name of the object
            is_text: Whether to create a text object

        Returns:
            New instance of the object if found, None otherwise
        """
        import copy
        
        if is_text:
            obj = self.get_text_object(name)
        else:
            obj = self.get_object(name)
        
        if obj:
            return copy.deepcopy(obj)
        
        return None