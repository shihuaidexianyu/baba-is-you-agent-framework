#!/usr/bin/env python3
"""
Simple demo agent for Baba Is You that can solve basic levels.
"""

from baba import create_environment


def main():
    """Play Baba Is You with a simple greedy agent."""
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

    print(f"Demo agent playing {env_name}...")

    # Game loop
    while True:
        # Find YOU and WIN objects
        you_objects = grid.rule_manager.get_you_objects()
        win_objects = grid.rule_manager.get_win_objects()

        if not you_objects:
            print("No controllable objects!")
            break

        # Find positions
        you_pos = None
        win_pos = None

        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if not obj.is_text:
                        if obj.name in you_objects and not you_pos:
                            you_pos = (x, y)
                        if obj.name in win_objects and not win_pos:
                            win_pos = (x, y)

        if not you_pos:
            print("Can't find YOU object position")
            break

        if not win_pos:
            print("No WIN object found")
            action = "wait"
        else:
            # Simple greedy movement towards WIN
            you_x, you_y = you_pos
            win_x, win_y = win_pos

            if win_x > you_x:
                action = "right"
            elif win_x < you_x:
                action = "left"
            elif win_y > you_y:
                action = "down"
            elif win_y < you_y:
                action = "up"
            else:
                action = "wait"

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
        if grid.steps > 50:
            print("Reached step limit")
            break


if __name__ == "__main__":
    main()
