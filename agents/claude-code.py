#!/usr/bin/env python3
"""
Claude Code agent for Baba Is You.
"""

import anyio
from claude_code_sdk import ClaudeCodeOptions, query

from baba import create_environment


async def get_action(state_description: str) -> str:
    """Ask Claude Code for the next action given the game state."""
    prompt = f"""You are playing Baba Is You. Analyze this game state and return ONLY a single action word.

{state_description}

Think step by step about what action to take, then respond with EXACTLY one word: up, down, left, right, or wait"""

    options = ClaudeCodeOptions(
        max_turns=1,
        system_prompt="You are an expert Baba Is You player. Respond with only single-word movement actions.",
    )

    response = ""
    async for message in query(prompt=prompt, options=options):
        # Extract text content from message
        if hasattr(message, "content"):
            response += message.content
        else:
            response += str(message)

    action = response.strip().lower()
    if action in ["up", "down", "left", "right", "wait"]:
        return action
    return "wait"


def describe_state(grid) -> str:
    """Convert game grid to text description."""
    lines = [f"Grid: {grid.width}x{grid.height}", f"Steps: {grid.steps}", "\nRules:"]

    for rule in grid.rule_manager.rules:
        lines.append(f"- {rule}")

    lines.append("\nObjects:")
    objects = {}
    for y in range(grid.height):
        for x in range(grid.width):
            for obj in grid.grid[y][x]:
                key = f"{obj.name} ({'text' if obj.is_text else 'object'})"
                if key not in objects:
                    objects[key] = []
                objects[key].append(f"({x},{y})")

    for obj_type, positions in sorted(objects.items()):
        lines.append(f"- {obj_type}: {', '.join(positions)}")

    you_objects = grid.rule_manager.get_you_objects()
    win_objects = grid.rule_manager.get_win_objects()

    if you_objects:
        lines.append(f"\nYOU: {', '.join(you_objects)}")
    if win_objects:
        lines.append(f"WIN: {', '.join(win_objects)}")

    return "\n".join(lines)


def main():
    """Play Baba Is You with Claude Code."""
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

    print(f"Claude Code playing {env_name}...")

    # Game loop
    while True:
        # Get action from Claude
        state = describe_state(grid)
        action = anyio.run(get_action, state)

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
