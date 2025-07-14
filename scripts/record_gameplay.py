#!/usr/bin/env python3
"""
Record gameplay and save as GIF.

This script plays an episode and captures frames to create a GIF.
"""

import os
from pathlib import Path

import pygame
from PIL import Image

from baba import EpisodePlayer, make


def record_gameplay(
    env_name: str = "simple",
    output_path: str = "gameplay.gif",
    cell_size: int = 32,
    fps: int = 10,
    max_frames: int = 100,
    duration_ms: int = 100,  # Duration per frame in GIF
):
    """
    Record gameplay and save as GIF.

    Args:
        env_name: Environment to record
        output_path: Path for output GIF
        cell_size: Size of each cell (smaller for GIF)
        fps: Frames per second during recording
        max_frames: Maximum frames to record
        duration_ms: Duration per frame in the GIF
    """
    print(f"Recording {env_name} gameplay...")

    # Create environment
    env = make(env_name)
    if not env:
        print(f"Environment '{env_name}' not found")
        return

    # Create a scripted agent for demo
    class DemoAgent:
        """Simple scripted agent for demo purposes."""

        def __init__(self, script):
            self.script = script
            self.step = 0
            self.name = "Demo Agent"

        def get_action(self, grid):  # noqa: ARG002
            if self.step < len(self.script):
                action = self.script[self.step]
                self.step += 1
                return action
            return None

        def reset(self):
            self.step = 0

    # Script for simple environment demo
    if env_name == "simple":
        # Move right to reach the flag
        script = ["right"] * 6 + [None]  # Move right 6 times then stop
    elif env_name == "push_puzzle":
        # Push rocks and reach flag
        script = ["right"] * 8 + [None]
    else:
        # Generic movement pattern
        script = ["right", "right", "down", "down", "left", "left", "up", "up"] + [None]

    agent = DemoAgent(script)

    # Initialize pygame
    pygame.init()

    # Create player with rendering
    player = EpisodePlayer(
        env=env, agent=agent, render=True, cell_size=cell_size, fps=fps, verbose=False
    )

    # Capture frames
    frames = []
    frame_count = 0

    # Setup for frame capture
    width = env.width * cell_size
    height = env.height * cell_size + 100  # Include UI area

    # Reset environment
    grid = env.reset()
    agent.reset()

    print("Capturing frames...")

    # Main game loop
    clock = pygame.time.Clock()
    done = False

    while not done and frame_count < max_frames:
        # Render current state
        player._render()

        # Capture frame
        screen = player.screen
        # Convert pygame surface to PIL Image
        frame_str = pygame.image.tostring(screen, "RGB")
        frame = Image.frombytes("RGB", (width, height), frame_str)
        frames.append(frame)
        frame_count += 1

        # Get action
        action = agent.get_action(grid)
        if action is None:
            done = True
        else:
            # Take action
            grid, won, lost = env.step(action)
            if won or lost:
                # Capture a few more frames to show the result
                for _ in range(5):
                    player._render()
                    frame_str = pygame.image.tostring(screen, "RGB")
                    frame = Image.frombytes("RGB", (width, height), frame_str)
                    frames.append(frame)
                done = True

        clock.tick(fps)

    pygame.quit()

    print(f"Captured {len(frames)} frames")

    # Save as GIF
    if frames:
        print(f"Saving GIF to {output_path}...")
        # Save with optimized palette
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )
        print(f"GIF saved! Size: {os.path.getsize(output_path) / 1024:.1f} KB")
    else:
        print("No frames captured!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Record Baba Is You gameplay as GIF")
    parser.add_argument("--env", default="simple", help="Environment to record (default: simple)")
    parser.add_argument(
        "--output", default="docs/gameplay.gif", help="Output GIF path (default: docs/gameplay.gif)"
    )
    parser.add_argument(
        "--cell-size", type=int, default=32, help="Cell size in pixels (default: 32)"
    )
    parser.add_argument("--fps", type=int, default=5, help="Recording FPS (default: 5)")
    parser.add_argument(
        "--max-frames", type=int, default=50, help="Maximum frames to record (default: 50)"
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True)

    record_gameplay(
        env_name=args.env,
        output_path=str(output_path),
        cell_size=args.cell_size,
        fps=args.fps,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
