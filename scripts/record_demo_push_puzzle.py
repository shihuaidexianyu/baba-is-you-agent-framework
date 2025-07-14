#!/usr/bin/env python3
"""
Record a demo agent playing push_puzzle for documentation.
"""

from agents.demo_agent import DemoAgent
from baba import create_environment


def main():
    """Record demo agent playing push_puzzle."""

    # Create environment
    env = create_environment("push_puzzle")

    # Create demo agent
    agent = DemoAgent()

    print("Recording demo agent playing push_puzzle...")

    # Play and record (with step limit for push puzzles)
    stats = agent.play_episode(
        env,
        render=True,
        record=True,
        record_path="docs/gameplay_push_puzzle_demo.gif",
        cell_size=48,
        fps=4,
        verbose=True,
        max_steps=100,  # Push puzzles can take many steps
    )

    if stats["won"]:
        print(f"\n✨ Won in {stats['steps']} steps!")
    else:
        print(f"\n❌ Didn't win (steps: {stats['steps']})")

    print("\nRecording saved to: docs/gameplay_push_puzzle_demo.gif")


if __name__ == "__main__":
    main()
