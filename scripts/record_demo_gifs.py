#!/usr/bin/env python3
"""
Record demonstration GIFs for the README.

Creates side-by-side gameplay recordings:
- Human playing simple level
- Claude playing complex level
"""

from pathlib import Path

from baba import create_environment
from baba.agent import ClaudeCodeAgent, UserAgent
from baba.episode_player import EpisodePlayer


def record_user_simple():
    """Record user playing simple environment."""
    print("\n=== Recording User Playing Simple Level ===")
    print("This will open a window. Play the game and win to create the recording.")
    print("Controls: Arrow keys to move, reach the flag to win!")

    env = create_environment("simple")
    agent = UserAgent()

    player = EpisodePlayer(
        env=env,
        agent=agent,
        render=True,
        cell_size=48,
        fps=10,
        verbose=True,
        record=True,
        record_path="docs/gameplay_user_simple.gif",
    )

    stats = player.play_episodes(1)

    if stats["wins"] > 0:
        print(f"✅ Recorded successful win in {stats['win_steps'][0]} steps!")
    else:
        print("❌ Recording captured, but level wasn't completed.")


def record_claude_complex():
    """Record Claude playing a complex environment."""
    print("\n=== Recording Claude Playing Complex Level ===")

    # Try different complex levels until we get a win
    complex_levels = ["rule_chain", "transform_puzzle", "make_win", "two_room_break_stop"]

    for level_name in complex_levels:
        print(f"\nTrying {level_name} environment...")

        env = create_environment(level_name)
        agent = ClaudeCodeAgent()

        player = EpisodePlayer(
            env=env,
            agent=agent,
            render=True,
            cell_size=48,
            fps=10,
            verbose=True,
            record=True,
            record_path=f"docs/gameplay_claude_{level_name}.gif",
        )

        stats = player.play_episodes(1)

        if stats["wins"] > 0:
            print(f"✨ Claude won {level_name} in {stats['win_steps'][0]} steps!")
            print(f"Recording saved to: docs/gameplay_claude_{level_name}.gif")
            return level_name
        else:
            print(f"Claude didn't win {level_name}, trying next...")

    print("\nClaude attempted all complex levels. Check recordings for the attempts.")
    return None


def main():
    """Record demo GIFs for README."""

    # Ensure docs directory exists
    Path("docs").mkdir(exist_ok=True)

    # Record user playing simple level
    record_user_simple()

    # Record Claude playing complex level
    winning_level = record_claude_complex()

    if winning_level:
        print("\n✅ Successfully recorded both demos!")
        print("User: docs/gameplay_user_simple.gif")
        print(f"Claude: docs/gameplay_claude_{winning_level}.gif")
    else:
        print("\n⚠️  Claude didn't win any of the complex levels.")
        print("Check the recorded attempts in the docs/ directory.")


if __name__ == "__main__":
    main()
