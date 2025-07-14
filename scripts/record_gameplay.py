#!/usr/bin/env python3
"""
Record gameplay and save as GIF.

This script plays an episode and captures frames to create a GIF.
"""

from pathlib import Path

from baba import Agent, make
from baba.grid import Grid


class ScriptedAgent(Agent):
    """Agent that follows a pre-defined script of actions."""

    def __init__(self, script: list[str], name: str = "Scripted Agent"):
        super().__init__(name)
        self.script = script
        self.step = 0

    def get_action(self, observation: Grid) -> str:  # noqa: ARG002
        """Get next action from script."""
        if self.step < len(self.script):
            action = self.script[self.step]
            self.step += 1
            return action
        return "wait"

    def reset(self):
        """Reset to start of script."""
        self.step = 0


def record_gameplay(
    env_name: str = "simple",
    output_path: str = "gameplay.gif",
    cell_size: int = 32,
    fps: int = 10,
    script: list[str] | None = None,
):
    """
    Record gameplay and save as GIF.

    Args:
        env_name: Environment to record
        output_path: Path for output GIF
        cell_size: Size of each cell (smaller for GIF)
        fps: Frames per second during recording
        script: List of actions to perform (auto-generated if None)
    """
    print(f"Recording {env_name} gameplay...")

    # Create environment
    env = make(env_name)
    if not env:
        print(f"Environment '{env_name}' not found")
        return

    # Create script if not provided
    if script is None:
        if env_name == "simple":
            # Move right to reach the flag
            script = ["right"] * 6
        elif env_name == "push_puzzle":
            # Push rocks and reach flag
            script = ["right"] * 8
        else:
            # Generic movement pattern
            script = ["right", "right", "down", "down", "left", "left", "up", "up"]

    # Create agent
    agent = ScriptedAgent(script, name=f"Demo {env_name}")

    # Record episode
    stats = agent.play_episode(
        env,
        render=True,
        record=True,
        record_path=output_path,
        cell_size=cell_size,
        fps=fps,
        verbose=True,
    )

    print("\nRecording complete!")
    print(f"Stats: {stats}")
    print(f"GIF saved to: {output_path}")


def main():
    """Run the recording script."""
    import argparse

    parser = argparse.ArgumentParser(description="Record Baba Is You gameplay as GIF")
    parser.add_argument("env", nargs="?", default="simple", help="Environment to record")
    parser.add_argument("-o", "--output", default="gameplay.gif", help="Output GIF path")
    parser.add_argument("--cell-size", type=int, default=32, help="Cell size in pixels")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second")

    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    record_gameplay(
        env_name=args.env,
        output_path=args.output,
        cell_size=args.cell_size,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
