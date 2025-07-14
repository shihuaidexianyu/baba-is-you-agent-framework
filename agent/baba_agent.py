#!/usr/bin/env python3
"""
Baba Is You Visual Agent Framework.

A programmable agent framework that runs Baba Is You with a visual GUI.
Designed to be extensible for tool use and advanced decision-making.
"""

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import os
import time
import json
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from collections import deque
from abc import ABC, abstractmethod

import numpy as np
import pygame

# Game imports
from baba import make
from baba.properties import Property


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class Action(Enum):
    """Available actions in the game."""
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    
    @classmethod
    def from_string(cls, s: str) -> Optional['Action']:
        """Convert string to Action."""
        s = s.lower().strip()
        for action in cls:
            if action.value == s or action.name.lower() == s:
                return action
        return None


@dataclass
class GameObservation:
    """Structured observation of the game state."""
    grid: Any  # The actual grid object from the environment
    controlled_objects: List[Dict[str, Any]]
    win_objects: List[Dict[str, Any]]
    pushable_objects: List[Dict[str, Any]]
    stop_objects: List[Dict[str, Any]]
    active_rules: List[str]
    grid_array: np.ndarray  # Visual representation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "controlled_objects": self.controlled_objects,
            "win_objects": self.win_objects,
            "pushable_objects": self.pushable_objects,
            "stop_objects": self.stop_objects,
            "active_rules": self.active_rules,
            "grid_shape": self.grid_array.shape[:2] if self.grid_array is not None else None
        }


@dataclass
class AgentDecision:
    """Represents an agent's decision."""
    action: Action
    reasoning: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ============================================================================
# DECISION MAKER INTERFACE
# ============================================================================

class DecisionMaker(ABC):
    """
    Abstract base class for decision-making components.
    
    This is the core extensibility point - implement this to create
    new types of decision makers (e.g., tool-using agents, LLM-based agents).
    """
    
    @abstractmethod
    def decide(self, observation: GameObservation) -> AgentDecision:
        """
        Make a decision based on the current game state.
        
        Args:
            observation: Structured observation of the game state
            
        Returns:
            AgentDecision with chosen action and reasoning
        """
        pass
    
    def reset(self):
        """Called when starting a new episode."""
        pass


# ============================================================================
# SIMPLE DECISION MAKERS
# ============================================================================

class SimplePathfindingDecisionMaker(DecisionMaker):
    """Basic decision maker using pathfinding and simple heuristics."""
    
    def decide(self, observation: GameObservation) -> AgentDecision:
        """Make decision using basic pathfinding."""
        # No controllable objects
        if not observation.controlled_objects:
            return AgentDecision(
                action=Action.RIGHT,
                reasoning="No controllable objects found, moving right to explore",
                confidence=0.2
            )
        
        # No win objects
        if not observation.win_objects:
            return self._explore_for_rules(observation)
        
        # Try direct path to win
        my_obj = observation.controlled_objects[0]
        my_pos = (my_obj['x'], my_obj['y'])
        
        for win_obj in observation.win_objects:
            win_pos = (win_obj['x'], win_obj['y'])
            path = self._find_path(observation, my_pos, win_pos)
            
            if path:
                return AgentDecision(
                    action=path[0],
                    reasoning=f"Moving toward {win_obj['type']} at {win_pos} ({len(path)} steps away)",
                    confidence=0.9
                )
        
        # Can't reach win directly
        return self._explore_for_rules(observation)
    
    def _explore_for_rules(self, observation: GameObservation) -> AgentDecision:
        """Explore to find text objects that might help."""
        # Look for nearby text objects
        text_objects = [obj for obj in observation.pushable_objects if obj.get('is_text', False)]
        
        if text_objects and observation.controlled_objects:
            my_obj = observation.controlled_objects[0]
            my_pos = (my_obj['x'], my_obj['y'])
            
            # Find nearest text
            nearest_text = min(text_objects, 
                             key=lambda t: abs(t['x'] - my_pos[0]) + abs(t['y'] - my_pos[1]))
            
            text_pos = (nearest_text['x'], nearest_text['y'])
            path = self._find_path(observation, my_pos, text_pos)
            
            if path:
                return AgentDecision(
                    action=path[0],
                    reasoning=f"Moving toward text '{nearest_text['type']}' to potentially modify rules",
                    confidence=0.7
                )
        
        # Default exploration
        return AgentDecision(
            action=Action.RIGHT,
            reasoning="Exploring the map to find opportunities",
            confidence=0.3
        )
    
    def _find_path(self, observation: GameObservation, start: Tuple[int, int], 
                   goal: Tuple[int, int]) -> List[Action]:
        """Simple BFS pathfinding."""
        if start == goal:
            return []
        
        # Get grid dimensions
        height, width = observation.grid_array.shape[:2]
        
        # BFS
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            # Try each direction
            for action in Action:
                new_pos = self._apply_action(pos, action)
                
                # Check bounds
                if not (0 <= new_pos[0] < width and 0 <= new_pos[1] < height):
                    continue
                
                # Check if visited
                if new_pos in visited:
                    continue
                
                # Check if blocked by STOP
                if self._is_blocked(observation, new_pos):
                    continue
                
                new_path = path + [action]
                
                # Found goal
                if new_pos == goal:
                    return new_path
                
                visited.add(new_pos)
                queue.append((new_pos, new_path))
        
        return []  # No path found
    
    def _apply_action(self, pos: Tuple[int, int], action: Action) -> Tuple[int, int]:
        """Apply action to position."""
        x, y = pos
        if action == Action.UP:
            return (x, y - 1)
        elif action == Action.DOWN:
            return (x, y + 1)
        elif action == Action.LEFT:
            return (x - 1, y)
        elif action == Action.RIGHT:
            return (x + 1, y)
    
    def _is_blocked(self, observation: GameObservation, pos: Tuple[int, int]) -> bool:
        """Check if position is blocked by STOP object."""
        return any(obj['x'] == pos[0] and obj['y'] == pos[1] 
                  for obj in observation.stop_objects)




# ============================================================================
# VISUAL AGENT
# ============================================================================

class BabaAgent:
    """
    Visual agent for playing Baba Is You.
    
    This is the main agent class that:
    - Manages the game environment
    - Renders the game visually using pygame
    - Delegates decisions to a DecisionMaker
    - Handles the game loop
    """
    
    def __init__(self, 
                 env_name: str = "simple",
                 decision_maker: Optional[DecisionMaker] = None,
                 cell_size: int = 48,
                 delay: float = 0.5,
                 show_info_panel: bool = True):
        """
        Initialize the visual agent.
        
        Args:
            env_name: Name of the environment to load
            decision_maker: DecisionMaker instance (defaults to SimplePathfindingDecisionMaker)
            cell_size: Size of each grid cell in pixels
            delay: Delay between actions in seconds
            show_info_panel: Whether to show the info panel
        """
        # Environment
        self.env = make(env_name)
        self.env_name = env_name
        
        # Decision making
        self.decision_maker = decision_maker or SimplePathfindingDecisionMaker()
        
        # Display settings
        self.cell_size = cell_size
        self.delay = delay
        self.show_info_panel = show_info_panel
        self.info_panel_height = 150 if show_info_panel else 0
        
        # Initialize pygame
        pygame.init()
        self._setup_display()
        
        # State tracking
        self.last_decision = None
        self.step_count = 0
        self.episode_count = 0
        
    # --- Core Methods ---
    
    def play_episode(self, max_steps: int = 100) -> bool:
        """
        Play one episode of the game.
        
        Args:
            max_steps: Maximum number of steps before timeout
            
        Returns:
            True if won, False otherwise
        """
        # Reset
        self.env.reset()
        self.decision_maker.reset()
        self.step_count = 0
        self.episode_count += 1
        
        # Initial render
        self._render()
        pygame.time.wait(1000)  # Show initial state
        
        # Game loop
        while self.step_count < max_steps:
            # Handle events
            if not self._handle_events():
                return False
            
            # Get observation
            observation = self._get_observation()
            
            # Make decision
            decision = self.decision_maker.decide(observation)
            self.last_decision = decision
            
            # Render current state
            self._render()
            
            # Delay
            pygame.time.wait(int(self.delay * 1000))
            
            # Execute action
            _, won, lost = self.env.step(decision.action.value)
            self.step_count += 1
            
            # Check if done
            if won:
                self._show_victory()
                return True
            elif lost:
                self._show_defeat()
                return False
        
        # Timeout
        self._show_timeout()
        return False
    
    def play_episodes(self, num_episodes: int = 1, max_steps: int = 100) -> Dict[str, Any]:
        """
        Play multiple episodes.
        
        Returns:
            Statistics about the episodes
        """
        wins = 0
        total_steps = 0
        
        for i in range(num_episodes):
            print(f"\nEpisode {i+1}/{num_episodes}")
            won = self.play_episode(max_steps)
            
            if won:
                wins += 1
            total_steps += self.step_count
            
            # Wait between episodes
            if i < num_episodes - 1:
                self._wait_for_key()
        
        return {
            "episodes": num_episodes,
            "wins": wins,
            "win_rate": wins / num_episodes if num_episodes > 0 else 0,
            "avg_steps": total_steps / num_episodes if num_episodes > 0 else 0
        }
    
    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()
    
    # --- Observation Methods ---
    
    def _get_observation(self) -> GameObservation:
        """Extract structured observation from game state."""
        grid = self.env.grid
        
        # Get objects by property
        controlled = self._find_objects_with_property(grid, Property.YOU)
        win_objects = self._find_objects_with_property(grid, Property.WIN)
        pushable = self._find_objects_with_property(grid, Property.PUSH)
        stops = self._find_objects_with_property(grid, Property.STOP)
        
        # Get active rules
        rules = []
        if hasattr(grid, 'rule_manager') and grid.rule_manager:
            rules = [str(rule) for rule in grid.rule_manager.rules]
        
        # Get visual array
        visual_array = self.env.render(self.cell_size)
        
        return GameObservation(
            grid=grid,
            controlled_objects=controlled,
            win_objects=win_objects,
            pushable_objects=pushable,
            stop_objects=stops,
            active_rules=rules,
            grid_array=visual_array
        )
    
    def _find_objects_with_property(self, grid, prop: Property) -> List[Dict[str, Any]]:
        """Find all objects with a given property."""
        objects = []
        
        for y in range(grid.height):
            for x in range(grid.width):
                cell_objects = grid.grid[y][x]
                for obj in cell_objects:
                    obj_name = obj.name.lower()
                    
                    # Check if has property
                    if grid.rule_manager and grid.rule_manager.has_property(obj_name, prop):
                        objects.append({
                            'type': obj_name,
                            'x': x,
                            'y': y,
                            'is_text': obj.is_text
                        })
                    
                    # Text is always pushable
                    elif prop == Property.PUSH and obj.is_text:
                        objects.append({
                            'type': obj_name,
                            'x': x,
                            'y': y,
                            'is_text': True
                        })
        
        return objects
    
    # --- Display Methods ---
    
    def _setup_display(self):
        """Set up the pygame display."""
        width = self.env.width * self.cell_size
        height = self.env.height * self.cell_size + self.info_panel_height
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Baba Agent - {self.env_name}")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
    
    def _render(self):
        """Render the current game state."""
        # Clear screen
        self.screen.fill((30, 30, 30))
        
        # Render game grid
        grid_image = self.env.render(self.cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        self.screen.blit(grid_surface, (0, 0))
        
        # Render info panel
        if self.show_info_panel:
            self._render_info_panel()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)
    
    def _render_info_panel(self):
        """Render the information panel."""
        y_base = self.env.height * self.cell_size + 10
        
        # Title
        title = f"🤖 {type(self.decision_maker).__name__} | Episode {self.episode_count} | Step {self.step_count}"
        title_surface = self.font.render(title, True, (255, 255, 255))
        self.screen.blit(title_surface, (10, y_base))
        
        # Last decision
        if self.last_decision:
            # Action
            action_text = f"Action: {self.last_decision.action.name}"
            action_surface = self.small_font.render(action_text, True, (150, 255, 150))
            self.screen.blit(action_surface, (10, y_base + 35))
            
            # Reasoning
            reasoning_text = f"Reasoning: {self.last_decision.reasoning[:80]}"
            if len(self.last_decision.reasoning) > 80:
                reasoning_text += "..."
            reasoning_surface = self.small_font.render(reasoning_text, True, (200, 200, 200))
            self.screen.blit(reasoning_surface, (10, y_base + 60))
            
            # Confidence
            conf_text = f"Confidence: {self.last_decision.confidence:.0%}"
            conf_color = (255, 200, 100) if self.last_decision.confidence > 0.7 else (255, 150, 150)
            conf_surface = self.small_font.render(conf_text, True, conf_color)
            self.screen.blit(conf_surface, (10, y_base + 85))
    
    def _show_victory(self):
        """Show victory animation."""
        self._render()
        
        # Victory text
        text = self.font.render("🎉 VICTORY! 🎉", True, (100, 255, 100))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, 
                                         self.screen.get_height() // 2))
        
        # Draw with background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 50, 0), bg_rect)
        pygame.draw.rect(self.screen, (100, 255, 100), bg_rect, 3)
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.wait(2000)
    
    def _show_defeat(self):
        """Show defeat animation."""
        self._render()
        
        text = self.font.render("❌ DEFEATED ❌", True, (255, 100, 100))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2,
                                         self.screen.get_height() // 2))
        
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (50, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 100, 100), bg_rect, 3)
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.wait(2000)
    
    def _show_timeout(self):
        """Show timeout message."""
        self._render()
        
        text = self.font.render("⏱️ TIME OUT ⏱️", True, (255, 255, 100))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2,
                                         self.screen.get_height() // 2))
        
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (50, 50, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 100), bg_rect, 3)
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.wait(2000)
    
    # --- Event Handling ---
    
    def _handle_events(self) -> bool:
        """Handle pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    # Pause
                    self._wait_for_key()
        return True
    
    def _wait_for_key(self):
        """Wait for a key press."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False
            self.clock.tick(30)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the agent."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Baba Is You Visual Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default pathfinding agent
  %(prog)s
  
  # Run specific environment
  %(prog)s --env make_win
  
  # Run multiple episodes
  %(prog)s --episodes 5 --env two_room
        """
    )
    
    parser.add_argument("--env", default="simple", 
                       help="Environment to play")
    parser.add_argument("--episodes", type=int, default=1,
                       help="Number of episodes to play")
    parser.add_argument("--max-steps", type=int, default=100,
                       help="Maximum steps per episode")
    parser.add_argument("--delay", type=float, default=0.5,
                       help="Delay between moves (seconds)")
    parser.add_argument("--no-info", action="store_true",
                       help="Hide the info panel")
    
    args = parser.parse_args()
    
    # Create decision maker
    decision_maker = SimplePathfindingDecisionMaker()
    
    # Create agent
    agent = BabaAgent(
        env_name=args.env,
        decision_maker=decision_maker,
        delay=args.delay,
        show_info_panel=not args.no_info
    )
    
    try:
        # Play episodes
        stats = agent.play_episodes(
            num_episodes=args.episodes,
            max_steps=args.max_steps
        )
        
        # Print summary
        print(f"\n{'='*40}")
        print(f"Summary:")
        print(f"  Episodes: {stats['episodes']}")
        print(f"  Wins: {stats['wins']}")
        print(f"  Win rate: {stats['win_rate']:.1%}")
        print(f"  Avg steps: {stats['avg_steps']:.1f}")
        print(f"{'='*40}")
        
    finally:
        agent.cleanup()


if __name__ == "__main__":
    main()