#!/usr/bin/env python3
"""
Random agent for Baba Is You.
"""

import random

from baba import create_environment


def main():
    """Play Baba Is You with random actions."""
    import sys

    # Get environment from command line or use default
    env_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        return

    # Reset to get initial state
    grid = env.reset()

    print(f"Random agent playing {env_name}...")

    # Game loop
    actions = ["up", "down", "left", "right", "wait"]

    while True:
        # Random action
        action = random.choice(actions)

        print(f"Step {grid.steps}: {action}")

        # Take action
        grid, won, lost = env.step(action)

        # Check game over
        if won:
            print(f"✅ Won in {grid.steps} steps!")
            break
        elif lost:
            print(f"❌ Lost after {grid.steps} steps")
            break

        # Safety limit
        if grid.steps > 100:
            print("Reached step limit")
            break


if __name__ == "__main__":
    main()
