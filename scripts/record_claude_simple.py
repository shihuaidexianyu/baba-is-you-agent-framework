#!/usr/bin/env python3
"""Record Claude Code agent playing simple level with reasoning display."""

from agents.claude_code_agent import ClaudeCodeAgent
from baba import create_environment


def main():
    """Record Claude Code agent on simple level."""

    # Create environment
    env = create_environment("simple")

    # Create Claude Code agent
    agent = ClaudeCodeAgent(verbose=True)

    print("Recording Claude Code agent playing simple level...")
    print("This will show Claude's reasoning in the UI")

    # Play and record
    stats = agent.play_episode(
        env,
        render=True,
        record=True,
        record_path="docs/gameplay_claude_simple_reasoning.gif",
        cell_size=48,
        fps=2,  # Slower to see reasoning
        verbose=True,
        max_steps=20,  # Simple level shouldn't take long
    )

    if stats["won"]:
        print(f"\n✨ Won in {stats['steps']} steps!")
    else:
        print(f"\n❌ Result: {stats}")

    print("\nRecording saved to: docs/gameplay_claude_simple_reasoning.gif")


if __name__ == "__main__":
    main()
