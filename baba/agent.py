"""
Agent interface for Baba Is You.

Simple and elegant agent system with just two implementations:
- UserAgent: Human player using keyboard input
- ClaudeCodeAgent: AI agent using Claude
"""

from abc import ABC, abstractmethod
from typing import Optional
import os

import pygame

from .grid import Grid


class Agent(ABC):
    """
    Abstract base class for all Baba Is You agents.
    
    Agents decide which action to take given the current game state.
    """
    
    def __init__(self, name: str = "Agent"):
        """
        Initialize the agent.
        
        Args:
            name: Display name for this agent
        """
        self.name = name
        
    @abstractmethod
    def get_action(self, grid: Grid) -> Optional[str]:
        """
        Choose an action given the current game state.
        
        Args:
            grid: Current game grid
            
        Returns:
            Action string ("up", "down", "left", "right", "wait") or None to quit
        """
        pass
        
    def reset(self):
        """
        Reset the agent for a new episode.
        
        Override this if your agent maintains internal state.
        """
        pass


class UserAgent(Agent):
    """
    Human player agent that gets actions from keyboard input.
    
    Controls:
    - Arrow keys or WASD: Movement
    - Space: Wait
    - R: Reset level (returns special action)
    - Q/ESC: Quit
    """
    
    def __init__(self):
        super().__init__("Human Player")
        self._quit_requested = False
        self._reset_requested = False
        
    def get_action(self, grid: Grid) -> Optional[str]:
        """
        Get action from keyboard input.
        
        Returns:
            Action string or None to quit
        """
        # Handle any pending requests
        if self._quit_requested:
            return None
        if self._reset_requested:
            self._reset_requested = False
            return "reset"
            
        # Wait for keyboard input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_requested = True
                    return None
                    
                elif event.type == pygame.KEYDOWN:
                    # Movement keys
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        return "up"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        return "down"
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        return "left"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        return "right"
                    elif event.key == pygame.K_SPACE:
                        return "wait"
                        
                    # Control keys
                    elif event.key == pygame.K_r:
                        self._reset_requested = True
                        return "reset"
                    elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        self._quit_requested = True
                        return None
                        
            # Small delay to prevent high CPU usage
            pygame.time.wait(10)


class ClaudeCodeAgent(Agent):
    """
    AI agent powered by Claude.
    
    Uses Claude's reasoning capabilities to:
    - Analyze the current game state
    - Understand active rules
    - Plan sequences of moves
    - Solve puzzles strategically
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__("Claude Code")
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        self._init_client()
        
    def _init_client(self):
        """Initialize the Anthropic client."""
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
            
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )
            
    def get_action(self, grid: Grid) -> Optional[str]:
        """
        Get action from Claude based on game state analysis.
        
        Returns:
            Action string or None to quit
        """
        # Convert game state to text description
        state_description = self._describe_game_state(grid)
        
        # Create prompt for Claude
        prompt = f"""You are playing Baba Is You. Analyze the current game state and choose the best action.

Current game state:
{state_description}

Available actions: up, down, left, right, wait

Think step by step:
1. What are the active rules?
2. What objects can I control (YOU property)?
3. What is the win condition (WIN property)?
4. What is the best move to make progress?

Respond with just the action word (up, down, left, right, or wait)."""

        # Get Claude's response
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract action from response
            action = response.content[0].text.strip().lower()
            
            # Validate action
            if action in ["up", "down", "left", "right", "wait"]:
                return action
            else:
                print(f"Invalid action from Claude: {action}, defaulting to wait")
                return "wait"
                
        except Exception as e:
            print(f"Error getting action from Claude: {e}")
            return "wait"
            
    def _describe_game_state(self, grid: Grid) -> str:
        """
        Convert grid state to text description for Claude.
        
        Returns:
            Text description of the game state
        """
        lines = []
        
        # Grid dimensions
        lines.append(f"Grid size: {grid.width}x{grid.height}")
        lines.append(f"Steps taken: {grid.steps}")
        
        # Active rules
        lines.append("\nActive rules:")
        for rule in grid.rule_manager.rules:
            lines.append(f"- {rule}")
            
        # Object positions
        lines.append("\nObject positions:")
        
        # Group objects by type
        object_positions = {}
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    key = f"{obj.name} ({'text' if obj.is_text else 'object'})"
                    if key not in object_positions:
                        object_positions[key] = []
                    object_positions[key].append(f"({x},{y})")
                    
        for obj_type, positions in sorted(object_positions.items()):
            lines.append(f"- {obj_type}: {', '.join(positions)}")
            
        # YOU and WIN objects
        you_objects = grid.rule_manager.get_you_objects()
        win_objects = grid.rule_manager.get_win_objects()
        
        if you_objects:
            lines.append(f"\nYOU objects: {', '.join(you_objects)}")
        if win_objects:
            lines.append(f"WIN objects: {', '.join(win_objects)}")
            
        return "\n".join(lines)
        
    def reset(self):
        """Reset any internal state."""
        pass