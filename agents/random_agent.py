"""
Random agent for Baba Is You.

This simple agent demonstrates the minimal Agent interface.
It just picks random actions.
"""

import random

from baba.agent import Agent
from baba.grid import Grid


class RandomAgent(Agent):
    """Agent that takes random actions."""

    def __init__(self):
        super().__init__("Random Agent")
        self.actions = ["up", "down", "left", "right", "wait"]

    def get_action(self, observation: Grid) -> str:  # noqa: ARG002
        """Pick a random action."""
        return random.choice(self.actions)


# Example usage
if __name__ == "__main__":
    from baba import create_environment

    # Create agent and environment
    agent = RandomAgent()
    env = create_environment("simple")

    # Play one episode with visualization
    stats = agent.play_episode(env, render=True, verbose=True)

    # Or play many episodes without visualization
    # stats = agent.play_episodes(env, num_episodes=100, render=False)
    # print(f"Win rate: {stats['win_rate']*100:.1f}%")
