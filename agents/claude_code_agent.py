#!/usr/bin/env python3
"""
Claude Code agent for Baba Is You.

This agent uses Claude's API to analyze the game state and decide on actions.
Requires claude-code-sdk to be installed.
"""

import asyncio

from claude_code_sdk import ClaudeCodeOptions, query

from baba.agent import Agent
from baba.grid import Grid


class ClaudeCodeAgent(Agent):
    """Agent that uses Claude Code API to play Baba Is You."""

    def __init__(self):
        super().__init__("Claude Code Agent")

    def get_action(self, observation: Grid) -> str:
        """
        Get action from Claude Code API.

        Args:
            observation: Current game state

        Returns:
            Action to take
        """
        # Describe the game state
        state_description = self._describe_state(observation)

        # Get action from Claude (run async function in sync context)
        action = asyncio.run(self._get_action_async(state_description))
        return action

    async def _get_action_async(self, state_description: str) -> str:
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

    def _describe_state(self, grid: Grid) -> str:
        """Convert game grid to text description."""
        lines = [f"Grid: {grid.width}x{grid.height}", f"Steps: {grid.steps}", "\nRules:"]

        for rule in grid.rule_manager.rules:
            lines.append(f"- {rule}")

        lines.append("\nObjects:")
        objects = {}

        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if not obj.is_text:
                        key = obj.name
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


# Example usage
if __name__ == "__main__":
    import sys

    from baba import create_environment

    # Get environment from command line or use default
    env_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        sys.exit(1)

    # Create agent and play
    agent = ClaudeCodeAgent()

    print("Claude Code playing Baba Is You...")
    print("Note: This requires a valid Claude API key")

    stats = agent.play_episode(env, render=True, verbose=True)
    print(f"\nFinal stats: {stats}")
