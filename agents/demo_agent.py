#!/usr/bin/env python3
"""
Simple demo agent for Baba Is You that can solve basic levels.
Uses greedy pathfinding to reach WIN objects.
"""

from baba.agent import Agent
from baba.grid import Grid


class DemoAgent(Agent):
    """Simple greedy agent that moves towards WIN objects."""

    def __init__(self):
        super().__init__("Demo Agent")

    def get_action(self, observation: Grid) -> str:
        """
        Choose action by moving greedily towards WIN objects.

        Args:
            observation: Current game state

        Returns:
            Action to take
        """
        # Find YOU and WIN objects
        you_objects = observation.rule_manager.get_you_objects()
        win_objects = observation.rule_manager.get_win_objects()

        if not you_objects:
            return "wait"  # No controllable objects

        # Find positions
        you_pos = None
        win_pos = None

        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text:
                        if obj.name in you_objects and not you_pos:
                            you_pos = (x, y)
                        if obj.name in win_objects and not win_pos:
                            win_pos = (x, y)

        if not you_pos or not win_pos:
            return "wait"  # Can't find positions

        # Simple greedy movement towards WIN
        you_x, you_y = you_pos
        win_x, win_y = win_pos

        if win_x > you_x:
            return "right"
        elif win_x < you_x:
            return "left"
        elif win_y > you_y:
            return "down"
        elif win_y < you_y:
            return "up"
        else:
            return "wait"


# Example usage
if __name__ == "__main__":
    import sys

    from baba import create_environment

    # Get environment from command line or use default
    env_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        sys.exit(1)

    # Create agent and play
    agent = DemoAgent()
    stats = agent.play_episode(env, render=True, verbose=True)

    print(f"\nFinal stats: {stats}")
