#!/usr/bin/env python3
"""
Record both demo agent and Claude Code agent on push_puzzle.
Shows the difference between simple pathfinding and reasoning AI.
"""

from agents.claude_code_agent import ClaudeCodeAgent
from agents.demo_agent import DemoAgent
from baba import create_environment


def record_agent(agent, env_name, output_path, max_steps=30):
    """Record an agent playing with a reasonable step limit."""

    # Create fresh environment
    env = create_environment(env_name)

    print(f"\nRecording {agent.name} on {env_name}...")

    # Play and record
    stats = agent.play_episode(
        env,
        render=True,
        record=True,
        record_path=output_path,
        cell_size=48,
        fps=8,  # Faster FPS to see time differences more clearly
        verbose=True,
        max_steps=max_steps,
    )

    if stats["won"]:
        print(f"✨ Won in {stats['steps']} steps!")
    elif stats["timeout"]:
        print(f"⏱️ Timeout after {stats['steps']} steps")
    else:
        print(f"❌ Lost after {stats['steps']} steps")

    return stats


def main():
    """Record both agents on push_puzzle."""

    print("=== Recording Push Puzzle Comparison ===")
    print("This will show how different agents handle pushing mechanics.")

    # Record demo agent (will get stuck quickly)
    demo_agent = DemoAgent()
    demo_stats = record_agent(
        demo_agent,
        "push_puzzle",
        "docs/gameplay_push_puzzle_demo_stuck.gif",
        max_steps=15,  # Short recording since it gets stuck
    )

    # Record Claude Code agent (should understand pushing)
    claude_agent = ClaudeCodeAgent(verbose=True)
    claude_stats = record_agent(
        claude_agent,
        "push_puzzle",
        "docs/gameplay_push_puzzle_claude.gif",
        max_steps=50,  # More steps for solving
    )

    print("\n=== Summary ===")
    print(
        f"Demo Agent: {'Won' if demo_stats['won'] else 'Did not win'} in {demo_stats['steps']} steps"
    )
    print(
        f"Claude Code Agent: {'Won' if claude_stats['won'] else 'Did not win'} in {claude_stats['steps']} steps"
    )
    print("\nRecordings saved to docs/")


if __name__ == "__main__":
    main()
