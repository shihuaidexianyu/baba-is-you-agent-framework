#!/usr/bin/env python3
"""
Record Claude playing complex levels for README showcase.

This script records Claude playing the rule_chain environment,
demonstrating advanced rule manipulation and strategic planning.
"""

from baba import create_environment
from baba.agent import ClaudeCodeAgent
from baba.episode_player import EpisodePlayer


def record_claude_gameplay():
    """Record Claude playing the rule_chain environment."""

    # Create environment
    env = create_environment("rule_chain")

    # Create Claude agent
    agent = ClaudeCodeAgent()

    # Create episode player with recording enabled
    player = EpisodePlayer(
        env=env,
        agent=agent,
        render=True,
        cell_size=48,
        fps=10,  # Slower FPS for better viewing
        verbose=True,
        record=True,
        record_path="docs/gameplay_rule_chain_claude.gif",
    )

    print("Recording Claude playing rule_chain environment...")
    print("This demonstrates advanced rule manipulation and planning.")

    # Play one episode
    stats = player.play_episodes(1)

    if stats["wins"] > 0:
        print(f"\n✨ Claude won in {stats['win_steps'][0]} steps!")
    else:
        print("\n❌ Claude didn't win this time. The recording still shows the attempt.")

    print("\nRecording saved to: docs/gameplay_rule_chain_claude.gif")


if __name__ == "__main__":
    record_claude_gameplay()
