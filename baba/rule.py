"""
Extracts and manages rules from a Baba Is You game grid.

This module handles the core rule system that defines object behavior:
- Extracting rules from text objects arranged in patterns
- Managing which objects have which properties (YOU, WIN, PUSH, etc.)
- Handling object transformations (ROCK IS BABA)

Rules are the heart of Baba Is You's gameplay mechanics.
"""

from typing import Dict, List, Optional, Set, Tuple

from .properties import Property
from .world_object import Object, TextObject, IsTextObject


class Rule:
    """
    Represents a rule in the game, e.g., 'BABA IS YOU'.
    
    Rules have three parts:
    - Subject: The object type the rule applies to (e.g., 'BABA')
    - Verb: Currently only 'IS' is supported
    - Complement: Either a property (YOU, WIN, etc.) or another object type
    
    Examples:
    - BABA IS YOU (gives BABA the YOU property)
    - FLAG IS WIN (gives FLAG the WIN property)
    - ROCK IS BABA (transforms all ROCKs into BABAs)
    """

    def __init__(self, subject: str, verb: str, complement: str):
        """
        Initialize a rule.

        Args:
            subject: The subject of the rule (e.g., 'BABA')
            verb: The verb of the rule (e.g., 'IS')
            complement: The complement of the rule (e.g., 'YOU')
        """
        self.subject = subject
        self.verb = verb
        self.complement = complement

    def __repr__(self):
        return f"{self.subject} {self.verb} {self.complement}"

    def __eq__(self, other):
        if isinstance(other, Rule):
            return (
                self.subject == other.subject
                and self.verb == other.verb
                and self.complement == other.complement
            )
        return False

    def __hash__(self):
        return hash((self.subject, self.verb, self.complement))


class RuleExtractor:
    """
    Extracts rules from the game grid by scanning for text patterns.
    
    Rules are formed when text objects are arranged in specific patterns:
    - Three consecutive text objects horizontally or vertically
    - Pattern: NOUN IS PROPERTY/NOUN
    - No gaps allowed between text objects
    
    The extractor scans the entire grid looking for these patterns.
    """

    def __init__(self, registry):
        """
        Initialize the rule extractor.

        Args:
            registry: The object registry to look up objects
        """
        self.registry = registry

    def extract_rules(self, grid: List[List[Set[Object]]]) -> List[Rule]:
        """
        Extract all active rules from the grid.
        
        Scans the grid in two passes:
        1. Horizontal scan: checks each row for rules reading left-to-right
        2. Vertical scan: checks each column for rules reading top-to-bottom
        
        Only complete, properly formed rules are extracted.

        Args:
            grid: The game grid

        Returns:
            List of active rules
        """
        rules = []
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        # Check horizontal rules
        for y in range(height):
            for x in range(width - 2):
                rule = self._check_rule_at(grid, x, y, dx=1, dy=0)
                if rule:
                    rules.append(rule)

        # Check vertical rules
        for y in range(height - 2):
            for x in range(width):
                rule = self._check_rule_at(grid, x, y, dx=0, dy=1)
                if rule:
                    rules.append(rule)

        return rules

    def _check_rule_at(
        self, grid: List[List[Set[Object]]], x: int, y: int, dx: int, dy: int
    ) -> Optional[Rule]:
        """
        Check if there's a valid rule at the given position in the given direction.
        
        Validation requirements:
        1. All three positions must contain text objects
        2. Middle position must be 'IS' verb
        3. First position must be a noun (object type)
        4. Third position must be either a property or noun

        Args:
            grid: The game grid
            x, y: Starting position
            dx, dy: Direction to check (1,0 for horizontal, 0,1 for vertical)

        Returns:
            A Rule if found, None otherwise
        """
        # Get objects at the three positions
        objects1 = grid[y][x]
        objects2 = grid[y + dy][x + dx]
        objects3 = grid[y + 2 * dy][x + 2 * dx]

        # Extract text objects
        text1 = self._get_text_object(objects1)
        text2 = self._get_text_object(objects2)
        text3 = self._get_text_object(objects3)

        if not all([text1, text2, text3]):
            return None

        # Validate rule structure:
        # Position 1: Must be a noun (object type like BABA, ROCK, etc.)
        if not hasattr(text1, "noun") or not text1.noun:
            return None
            
        # Position 2: Must be the verb IS
        if not (hasattr(text2, "verb") and text2.verb and text2.verb.lower() == "is"):
            return None

        # Position 3: Can be either a property or another noun
        if hasattr(text3, "property") and text3.property:
            # Property rule (e.g., BABA IS YOU)
            # The property.value gives us the string representation
            return Rule(text1.noun.upper(), "IS", text3.property.value)
        elif hasattr(text3, "noun") and text3.noun:
            # Transformation rule (e.g., BABA IS ROCK)
            # Both subject and complement are uppercased for consistency
            return Rule(text1.noun.upper(), "IS", text3.noun.upper())

        return None

    def _get_text_object(self, objects: Set[Object]) -> Optional[TextObject]:
        """Get the text object from a set of objects, if any."""
        for obj in objects:
            if isinstance(obj, TextObject):
                return obj
        return None


class RuleManager:
    """
    Manages active rules and their effects on game objects.
    
    The RuleManager is responsible for:
    - Storing the current set of active rules
    - Computing which objects have which properties
    - Determining object transformations
    - Answering queries about object behavior
    
    When rules change (e.g., text is moved), the manager recomputes
    all properties and transformations.
    """

    def __init__(self):
        """Initialize the rule manager."""
        self.rules: List[Rule] = []  # All active rules
        # Maps object names to their properties (e.g., {'BABA': {Property.YOU}})
        self.properties: Dict[str, Set[Property]] = {}
        # Maps object names to what they transform into (e.g., {'ROCK': 'BABA'})
        self.transformations: Dict[str, str] = {}

    def update_rules(self, rules: List[Rule]):
        """
        Update the active rules and recompute properties and transformations.
        
        This is called whenever the grid changes (after movement or transformation)
        to ensure rules reflect the current text arrangement.

        Args:
            rules: List of active rules extracted from the grid
        """
        self.rules = rules
        self._compute_properties()
        self._compute_transformations()

    def _compute_properties(self):
        """
        Compute object properties from rules.
        
        Processes each rule and assigns properties to objects.
        Properties are defined in the Property enum (YOU, WIN, PUSH, etc.).
        """
        self.properties.clear()

        for rule in self.rules:
            if rule.verb == "IS":
                # Try to parse complement as a property
                try:
                    # Property enum will raise ValueError if not a valid property
                    prop = Property(rule.complement)
                    if rule.subject not in self.properties:
                        self.properties[rule.subject] = set()
                    self.properties[rule.subject].add(prop)
                except ValueError:
                    # Not a property, likely a transformation (e.g., ROCK IS BABA)
                    pass

    def _compute_transformations(self):
        """
        Compute object transformations from rules.
        
        Identifies rules where the complement is another object type
        rather than a property (e.g., ROCK IS BABA).
        """
        self.transformations.clear()

        for rule in self.rules:
            if rule.verb == "IS":
                # Check if complement is not a property (i.e., it's a noun)
                try:
                    Property(rule.complement)
                    # If no exception, it's a property, not a transformation
                except ValueError:
                    # Not a valid property, so it must be a transformation
                    # Store the transformation target
                    self.transformations[rule.subject] = rule.complement

    def get_properties(self, object_name: str) -> Set[Property]:
        """
        Get all properties for a given object type.

        Args:
            object_name: Name of the object type (e.g., 'BABA')

        Returns:
            Set of properties for the object
        """
        return self.properties.get(object_name.upper(), set())

    def get_transformation(self, object_name: str) -> Optional[str]:
        """
        Get the transformation for a given object type.

        Args:
            object_name: Name of the object type

        Returns:
            The object type to transform into, or None
        """
        return self.transformations.get(object_name.upper())

    def has_property(self, object_name: str, property: Property) -> bool:
        """
        Check if an object type has a specific property.
        
        This is the primary method used during gameplay to determine
        object behavior (can it move? does it block? etc.)

        Args:
            object_name: Name of the object type (case-insensitive)
            property: The property to check

        Returns:
            True if the object has the property
        """
        return property in self.get_properties(object_name)

    def get_you_objects(self) -> List[str]:
        """
        Get all object types that have the YOU property.

        Returns:
            List of object type names
        """
        return [
            obj_name
            for obj_name, props in self.properties.items()
            if Property.YOU in props
        ]

    def get_win_objects(self) -> List[str]:
        """
        Get all object types that have the WIN property.

        Returns:
            List of object type names
        """
        return [
            obj_name
            for obj_name, props in self.properties.items()
            if Property.WIN in props
        ]

    def get_push_objects(self) -> List[str]:
        """
        Get all object types that have the PUSH property.

        Returns:
            List of object type names
        """
        return [
            obj_name
            for obj_name, props in self.properties.items()
            if Property.PUSH in props
        ]

    def get_stop_objects(self) -> List[str]:
        """
        Get all object types that have the STOP property.

        Returns:
            List of object type names
        """
        return [
            obj_name
            for obj_name, props in self.properties.items()
            if Property.STOP in props
        ]

    def get_sink_objects(self) -> List[str]:
        """
        Get all object types that have the SINK property.

        Returns:
            List of object type names
        """
        return [
            obj_name
            for obj_name, props in self.properties.items()
            if Property.SINK in props
        ]