#!/usr/bin/env python3
"""
Claude Code agent for Baba Is You.

This agent uses Claude's API to analyze the game state and decide on actions.
Requires claude-code-sdk to be installed.
"""

import asyncio
import time

from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    TextBlock,
    query,
)

from baba.agent import Agent
from baba.grid import Grid


class ClaudeCodeAgent(Agent):
    """Agent that uses Claude Code API to play Baba Is You."""

    def __init__(self, verbose=True):
        super().__init__("Claude Code Agent")
        self.verbose = verbose
        self.conversation_history = []  # Track conversation for context
        self.episode_steps = 0
        self.session_active = False

    def reset(self):  # noqa: B027
        """Reset the agent for a new episode."""
        self.conversation_history = []
        self.episode_steps = 0
        self.session_active = False
        if self.verbose:
            print("\n=== Starting new Claude Code session ===")

    def get_action(self, observation: Grid) -> str:
        """
        Get action from Claude Code API.

        Args:
            observation: Current game state

        Returns:
            Action to take
        """
        self.episode_steps += 1

        # Describe the game state
        state_description = self._describe_state(observation)

        # Get action from Claude
        action = asyncio.run(self._get_action_async(state_description, observation))
        return action

    async def _get_action_async(self, state_description: str, observation: Grid) -> str:
        """Ask Claude Code for the next action given the game state."""
        # Build minimal prompt for speed
        if self.episode_steps == 1:
            prompt = f"""Baba Is You game. Respond with just one movement word.

{state_description}

ACTION: """
        else:
            prompt = f"""Step {self.episode_steps}:
{state_description}

ACTION: """

        # Use continue_conversation after first message
        options = ClaudeCodeOptions(
            max_turns=1,
            system_prompt="You are playing Baba Is You. Respond with only movement words: up, down, left, right. Never use 'wait'. Be fast and decisive.",
            continue_conversation=self.session_active,
            permission_mode="bypassPermissions",  # No prompts during game
        )

        response = ""
        start_time = time.time()
        timeout = 10.0  # 10 second timeout per move

        try:
            async for message in query(prompt=prompt, options=options):
                # Check timeout
                if time.time() - start_time > timeout:
                    if self.verbose:
                        print(f"\n[Step {self.episode_steps}] Timeout after {timeout}s")
                    break

                # Extract text content from message
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response += block.text
        except Exception as e:
            if self.verbose:
                print(f"\n[Step {self.episode_steps}] Error: {e}")
            response = ""

        # Mark session as active after first query
        self.session_active = True

        if self.verbose and response:
            print(f"\n[Step {self.episode_steps}] Claude: {response.strip()}")

        # Extract action from response
        action = None
        response_lower = response.strip().lower()

        # Look for ACTION: line first
        for line in response_lower.split("\n"):
            if "action:" in line:
                remaining = line.split("action:")[1].strip()
                for direction in ["up", "down", "left", "right"]:
                    if direction in remaining:
                        action = direction
                        break
                if action:
                    break

        # If no ACTION: line, look for direction words
        if not action:
            for direction in ["up", "down", "left", "right"]:
                if direction in response_lower:
                    action = direction
                    break

        # Last resort - pick a direction based on goal position
        if not action:
            you_objects = observation.rule_manager.get_you_objects()
            win_objects = observation.rule_manager.get_win_objects()

            if you_objects and win_objects:
                # Find positions
                you_pos = None
                win_pos = None

                for y in range(observation.height):
                    for x in range(observation.width):
                        for obj in observation.grid[y][x]:
                            if obj.name.lower() in you_objects and not you_pos:
                                you_pos = (x, y)
                            if obj.name.lower() in win_objects and not win_pos:
                                win_pos = (x, y)

                if you_pos and win_pos:
                    dx = win_pos[0] - you_pos[0]
                    dy = win_pos[1] - you_pos[1]

                    if abs(dx) > abs(dy):
                        action = "right" if dx > 0 else "left"
                    else:
                        action = "down" if dy > 0 else "up"

            if not action:
                import random

                action = random.choice(["up", "down", "left", "right"])

            if self.verbose:
                print(f"(No clear action found, choosing: {action})")

        if self.verbose:
            print(f">>> Action: {action}")

        # Store action in history
        self.conversation_history.append((action, "taken"))

        return action

    def _describe_state(self, grid: Grid) -> str:
        """Convert game grid to text description - ultra concise."""
        lines = []

        # Compact grid visualization
        lines.append("Grid:")
        for y in range(grid.height):
            row = []
            for x in range(grid.width):
                cell_objs = list(grid.grid[y][x])
                if not cell_objs:
                    row.append(".")
                else:
                    obj = cell_objs[0]
                    if obj.is_text:
                        row.append(obj.name[0].upper())
                    else:
                        row.append(obj.name[0].lower())
            lines.append("".join(row))

        # Key info only
        you_objects = grid.rule_manager.get_you_objects()
        win_objects = grid.rule_manager.get_win_objects()

        lines.append(f"YOU: {you_objects[0] if you_objects else 'none'}")
        lines.append(f"WIN: {win_objects[0] if win_objects else 'none'}")

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
    agent = ClaudeCodeAgent(verbose=True)

    print("Claude Code playing Baba Is You...")
    print("Using continue_conversation for faster responses")

    stats = agent.play_episode(env, render=True, verbose=True)
    print(f"\nFinal stats: {stats}")
