"""Test suite for rule parsing and property system."""

import pytest
from baba.grid import Grid
from baba.registration import Registry
from baba.properties import Property
from baba.rule import Rule, RuleManager, RuleExtractor


class TestRuleParsing:
    """Test rule extraction and parsing."""
    
    @pytest.fixture
    def rule_setup(self):
        """Set up grid with rule extraction."""
        registry = Registry()
        grid = Grid(10, 10, registry)
        return grid, registry
    
    def test_simple_noun_is_property_rule(self, rule_setup):
        """Test basic NOUN IS PROPERTY rule formation."""
        grid, registry = rule_setup
        
        # Create BABA IS YOU
        baba_text = registry.create_instance("baba", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        you_text = registry.create_instance("you", is_text=True)
        
        grid.place_object(baba_text, 1, 1)
        grid.place_object(is_text, 2, 1)
        grid.place_object(you_text, 3, 1)
        
        grid._update_rules()
        
        assert grid.rule_manager.has_property("baba", Property.YOU)
        assert "BABA" in grid.rule_manager.get_you_objects()
    
    def test_vertical_rule_parsing(self, rule_setup):
        """Test vertical rule formation."""
        grid, registry = rule_setup
        
        # Create vertical ROCK IS WIN
        rock_text = registry.create_instance("rock", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        win_text = registry.create_instance("win", is_text=True)
        
        grid.place_object(rock_text, 5, 3)
        grid.place_object(is_text, 5, 4)
        grid.place_object(win_text, 5, 5)
        
        grid._update_rules()
        
        assert grid.rule_manager.has_property("rock", Property.WIN)
        assert "ROCK" in grid.rule_manager.get_win_objects()
    
    def test_multiple_rules(self, rule_setup):
        """Test multiple rules can coexist."""
        grid, registry = rule_setup
        
        # BABA IS YOU
        grid.place_object(registry.create_instance("baba", is_text=True), 1, 1)
        grid.place_object(registry.create_instance("is", is_text=True), 2, 1)
        grid.place_object(registry.create_instance("you", is_text=True), 3, 1)
        
        # ROCK IS PUSH
        grid.place_object(registry.create_instance("rock", is_text=True), 1, 3)
        grid.place_object(registry.create_instance("is", is_text=True), 2, 3)
        grid.place_object(registry.create_instance("push", is_text=True), 3, 3)
        
        # WALL IS STOP
        grid.place_object(registry.create_instance("wall", is_text=True), 1, 5)
        grid.place_object(registry.create_instance("is", is_text=True), 2, 5)
        grid.place_object(registry.create_instance("stop", is_text=True), 3, 5)
        
        grid._update_rules()
        
        assert grid.rule_manager.has_property("baba", Property.YOU)
        assert grid.rule_manager.has_property("rock", Property.PUSH)
        assert grid.rule_manager.has_property("wall", Property.STOP)
    
    def test_noun_is_noun_transformation(self, rule_setup):
        """Test NOUN IS NOUN transformation rules."""
        grid, registry = rule_setup
        
        # Create BABA IS ROCK
        baba_text = registry.create_instance("baba", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        rock_text = registry.create_instance("rock", is_text=True)
        
        grid.place_object(baba_text, 1, 1)
        grid.place_object(is_text, 2, 1)
        grid.place_object(rock_text, 3, 1)
        
        grid._update_rules()
        
        transformation = grid.rule_manager.get_transformation("baba")
        assert transformation == "ROCK"
    
    def test_broken_rule_not_parsed(self, rule_setup):
        """Test incomplete rules are not parsed."""
        grid, registry = rule_setup
        
        # Create incomplete rule: BABA IS (missing property)
        baba_text = registry.create_instance("baba", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        
        grid.place_object(baba_text, 1, 1)
        grid.place_object(is_text, 2, 1)
        
        grid._update_rules()
        
        # Should have no rules
        assert len(grid.rule_manager.rules) == 0
    
    def test_misaligned_rule_not_parsed(self, rule_setup):
        """Test misaligned text doesn't form rules."""
        grid, registry = rule_setup
        
        # Create misaligned ROCK IS WIN
        rock_text = registry.create_instance("rock", is_text=True)
        is_text = registry.create_instance("is", is_text=True)
        win_text = registry.create_instance("win", is_text=True)
        
        grid.place_object(rock_text, 1, 1)
        grid.place_object(is_text, 2, 2)  # Not aligned
        grid.place_object(win_text, 3, 1)
        
        grid._update_rules()
        
        # Should not recognize the rule
        assert not grid.rule_manager.has_property("rock", Property.WIN)
    
    def test_rule_with_gap_not_parsed(self, rule_setup):
        """Test rules with gaps are not parsed."""
        grid, registry = rule_setup
        
        # Create BABA _ YOU (gap where IS should be)
        baba_text = registry.create_instance("baba", is_text=True)
        you_text = registry.create_instance("you", is_text=True)
        
        grid.place_object(baba_text, 1, 1)
        # No IS at (2, 1)
        grid.place_object(you_text, 3, 1)
        
        grid._update_rules()
        
        assert not grid.rule_manager.has_property("baba", Property.YOU)
    
    def test_rule_overrides(self, rule_setup):
        """Test that newer rules override older ones."""
        grid, registry = rule_setup
        
        # First make BABA IS YOU
        grid.place_object(registry.create_instance("baba", is_text=True), 1, 1)
        grid.place_object(registry.create_instance("is", is_text=True), 2, 1)
        grid.place_object(registry.create_instance("you", is_text=True), 3, 1)
        
        grid._update_rules()
        assert grid.rule_manager.has_property("baba", Property.YOU)
        
        # Now make ROCK IS YOU (should replace BABA IS YOU)
        grid.place_object(registry.create_instance("rock", is_text=True), 1, 3)
        grid.place_object(registry.create_instance("is", is_text=True), 2, 3)
        grid.place_object(registry.create_instance("you", is_text=True), 3, 3)
        
        # Remove the BABA IS YOU rule
        grid.remove_object(grid.get_objects_at(3, 1).pop(), 3, 1)
        
        grid._update_rules()
        assert not grid.rule_manager.has_property("baba", Property.YOU)
        assert grid.rule_manager.has_property("rock", Property.YOU)


class TestRuleManager:
    """Test the RuleManager directly."""
    
    def test_rule_manager_initialization(self):
        """Test RuleManager starts empty."""
        manager = RuleManager()
        assert len(manager.rules) == 0
        assert len(manager.get_you_objects()) == 0
        assert len(manager.get_win_objects()) == 0
    
    def test_add_and_query_rules(self):
        """Test adding rules and querying properties."""
        manager = RuleManager()
        
        rule1 = Rule("BABA", "IS", "YOU")
        rule2 = Rule("ROCK", "IS", "PUSH")
        rule3 = Rule("FLAG", "IS", "WIN")
        
        manager.update_rules([rule1, rule2, rule3])
        
        assert manager.has_property("baba", Property.YOU)
        assert manager.has_property("rock", Property.PUSH)
        assert manager.has_property("flag", Property.WIN)
        assert not manager.has_property("wall", Property.STOP)
    
    def test_get_objects_by_property(self):
        """Test retrieving objects by property."""
        manager = RuleManager()
        
        rules = [
            Rule("BABA", "IS", "YOU"),
            Rule("ME", "IS", "YOU"),
            Rule("ROCK", "IS", "PUSH"),
            Rule("FLAG", "IS", "WIN"),
            Rule("LAVA", "IS", "WIN")
        ]
        
        manager.update_rules(rules)
        
        you_objects = manager.get_you_objects()
        assert len(you_objects) == 2
        assert "BABA" in you_objects
        assert "ME" in you_objects
        
        win_objects = manager.get_win_objects()
        assert len(win_objects) == 2
        assert "FLAG" in win_objects
        assert "LAVA" in win_objects
    
    def test_clear_rules(self):
        """Test clearing all rules."""
        manager = RuleManager()
        
        manager.update_rules([Rule("BABA", "IS", "YOU")])
        assert len(manager.rules) == 1
        
        manager.update_rules([])
        assert len(manager.rules) == 0
        assert not manager.has_property("baba", Property.YOU)