#!/usr/bin/env python3
"""
Create demo recordings for the README.
"""

from pathlib import Path

from baba import create_environment
from baba.agent import Agent
from baba.episode_player import EpisodePlayer


class DemoAgent(Agent):
    """Simple greedy agent for demos."""

    def __init__(self):
        super().__init__("Demo Agent")

    def get_action(self, grid):
        """Simple pathfinding to WIN."""
        # Find YOU and WIN objects
        you_objects = grid.rule_manager.get_you_objects()
        win_objects = grid.rule_manager.get_win_objects()

        if not you_objects:
            return "wait"

        # Find positions
        you_pos = None
        win_pos = None

        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if not obj.is_text:
                        if obj.name.upper() in you_objects and not you_pos:
                            you_pos = (x, y)
                        if obj.name.upper() in win_objects and not win_pos:
                            win_pos = (x, y)

        if not you_pos or not win_pos:
            return "wait"

        # Simple greedy movement
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


def record_demo_agent():
    """Record the demo agent playing."""
    print("\n=== Recording Demo Agent ===")

    # Create environment
    env = create_environment("simple")
    agent = DemoAgent()

    # Add step limit
    original_step = env.step
    step_count = 0

    def limited_step(action):
        nonlocal step_count
        step_count += 1
        grid, won, lost = original_step(action)
        if step_count >= 20:  # Max 20 steps
            print(f"Reached step limit: {step_count}")
            lost = True
        return grid, won, lost

    env.step = limited_step

    # Create player with recording
    player = EpisodePlayer(
        env=env,
        agent=agent,
        render=True,
        cell_size=48,
        fps=10,
        verbose=True,
        record=True,
        record_path="docs/gameplay_demo.gif",
    )

    # Play episode
    stats = player.play_episodes(1)

    if stats["wins"] > 0:
        print(f"✅ Demo agent won in {stats['win_steps'][0]} steps!")
        return True
    else:
        print(f"❌ Demo agent didn't win (steps: {step_count})")
        return False


def record_claude_code():
    """Record Claude Code agent playing."""
    print("\n=== Recording Claude Code Agent ===")

    # Import claude-code agent module
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "claude_code_agent", "agents/claude_code_agent.py"
    )
    claude_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(claude_module)

    # Create environment
    env = create_environment("push_puzzle")
    agent = claude_module.ClaudeCodeAgent()

    # Create player with recording
    player = EpisodePlayer(
        env=env,
        agent=agent,
        render=True,
        cell_size=48,
        fps=10,
        verbose=True,
        record=True,
        record_path="docs/gameplay_claude_code.gif",
    )

    # Play episode with step limit
    original_step = env.step
    step_count = 0

    def limited_step(action):
        nonlocal step_count
        step_count += 1
        grid, won, lost = original_step(action)
        if step_count > 30:  # Limit to 30 steps
            lost = True
        return grid, won, lost

    env.step = limited_step

    try:
        stats = player.play_episodes(1)

        if stats["wins"] > 0:
            print(f"✅ Claude Code won in {stats['win_steps'][0]} steps!")
            return True
        else:
            print(f"Recording complete after {step_count} steps")
            return False
    except Exception as e:
        print(f"Error during Claude Code recording: {e}")
        return False


def main():
    """Create demo recordings."""
    # Ensure docs directory exists
    Path("docs").mkdir(exist_ok=True)

    # Record demo agent
    demo_success = record_demo_agent()

    # Record Claude Code agent
    print("\nNote: Claude Code recording requires the Claude Code SDK to be running.")
    print("It will use the actual Claude Code agent implementation.")

    try:
        claude_success = record_claude_code()
    except Exception as e:
        print(f"Could not record Claude Code: {e}")
        claude_success = False

    print("\n=== Recording Summary ===")
    if demo_success:
        print("✅ Demo agent recording: docs/gameplay_demo.gif")
    if claude_success:
        print("✅ Claude Code recording: docs/gameplay_claude_code.gif")

    if not demo_success and not claude_success:
        print("❌ No successful recordings created")


if __name__ == "__main__":
    main()
