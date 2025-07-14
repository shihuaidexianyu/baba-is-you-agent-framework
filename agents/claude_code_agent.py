#!/usr/bin/env python3
"""
Claude Code agent for Baba Is You.

This agent uses Claude's API to analyze the game state and decide on actions.
Requires claude-code-sdk to be installed.
"""

import asyncio
import json
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
        self.last_reasoning = "Starting game..."  # Store reasoning for UI display

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
            prompt = f"""Baba Is You puzzle. Remember: YOU must touch WIN to win. You can push objects.

{state_description}

What's your move? Respond with only JSON:
{{"action": "right", "reasoning": "move toward flag"}}

Your JSON response: """
        else:
            prompt = f"""Step {self.episode_steps}:
{state_description}

Next move as JSON: """

        # Use continue_conversation after first message
        options = ClaudeCodeOptions(
            max_turns=1,
            system_prompt='You are playing Baba Is You. To win: move YOUR object to touch a WIN object. You can push objects and text. Pushing text changes rules. ALWAYS respond with only valid JSON: {"action": "<direction>", "reasoning": "<brief explanation>"}. Direction must be one of: up, down, left, right.',
            continue_conversation=self.session_active,
            permission_mode="bypassPermissions",  # No prompts during game
        )

        response = ""
        start_time = time.time()
        timeout = 30.0  # 30 second timeout per move (more time for complex puzzles)

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

        if self.verbose:
            if response:
                print(f"\n[Step {self.episode_steps}] Claude response: '{response.strip()}'")
            else:
                print(f"\n[Step {self.episode_steps}] Claude returned empty response!")

        # Extract action and reasoning from JSON response
        action = None
        reasoning = "Thinking..."

        # Try to parse JSON
        try:
            # Find JSON in response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                action = data.get("action", "").lower()
                reasoning = data.get("reasoning", "No reasoning provided")
                if action not in ["up", "down", "left", "right"]:
                    action = None
        except Exception as e:
            if self.verbose:
                print(f"JSON parse error: {e}")
            # Fallback to looking for direction words
            response_lower = response.strip().lower()
            for direction in ["up", "down", "left", "right"]:
                if direction in response_lower:
                    action = direction
                    reasoning = "Quick decision"
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

            reasoning = f"No clear path, trying {action}"
            self.last_reasoning = reasoning

            if self.verbose:
                print(f"(No clear action found, choosing: {action})")

        # Store reasoning for UI display
        self.last_reasoning = reasoning

        if self.verbose:
            print(f">>> Action: {action} | Reasoning: {reasoning}")
            if action is None:
                print(">>> Failed to parse response, falling back to heuristic")

        # Store action in history
        self.conversation_history.append((action, "taken"))

        return action

    def _describe_state(self, grid: Grid) -> str:
        """Convert game grid to clear text description."""
        lines = []

        # Important game mechanics reminder
        lines.append("GAME RULES: To win, YOU must touch an object that IS WIN.")
        lines.append("You can push objects and text. Pushing text can change rules.")
        lines.append("")

        # Current rules
        lines.append("Active Rules:")
        for rule in grid.rule_manager.rules:
            lines.append(f"  {rule}")

        # What YOU control and what is WIN
        you_objects = grid.rule_manager.get_you_objects()
        win_objects = grid.rule_manager.get_win_objects()
        push_objects = grid.rule_manager.get_push_objects()
        stop_objects = grid.rule_manager.get_stop_objects()

        lines.append("")
        lines.append(f"YOU control: {', '.join(you_objects) if you_objects else 'nothing'}")
        lines.append(f"WIN objects: {', '.join(win_objects) if win_objects else 'nothing'}")
        lines.append(f"PUSH objects: {', '.join(push_objects) if push_objects else 'nothing'}")
        lines.append(f"STOP objects: {', '.join(stop_objects) if stop_objects else 'nothing'}")

        # Grid representation
        lines.append("\nGrid Layout:")
        lines.append("- Empty cells: .")
        lines.append("- Objects (game pieces): lowercase (e.g., baba, rock, flag)")
        lines.append("- Text (rule pieces): UPPERCASE (e.g., BABA, IS, YOU)")
        lines.append("")

        # Find max object name length for proper spacing
        max_len = 4  # Minimum width
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    max_len = max(max_len, len(obj.name))

        # Add column numbers for reference
        col_header = "   "
        for x in range(grid.width):
            col_header += str(x).center(max_len + 1)
        lines.append(col_header)
        lines.append("   " + "-" * (grid.width * (max_len + 1)))

        # Build grid with proper spacing
        for y in range(grid.height):
            row_str = f"{y}| "
            for x in range(grid.width):
                cell_objs = list(grid.grid[y][x])
                if not cell_objs:
                    row_str += ".".center(max_len) + " "
                else:
                    # If multiple objects in cell, show first one
                    obj = cell_objs[0]
                    if obj.is_text:
                        # Remove _TEXT suffix for clarity
                        name = obj.name.upper()
                        if name.endswith("_TEXT"):
                            name = name[:-5]
                    else:
                        name = obj.name.lower()
                    row_str += name.center(max_len) + " "
            lines.append(row_str.rstrip())

        # Add legend for what's in the grid
        lines.append("\nObjects in grid:")
        # Collect all unique objects
        objects_set = set()
        texts_set = set()
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if obj.is_text:
                        name = obj.name.upper()
                        if name.endswith("_TEXT"):
                            name = name[:-5]
                        texts_set.add(name)
                    else:
                        objects_set.add(obj.name.lower())

        if objects_set:
            lines.append(f"  Game objects: {', '.join(sorted(objects_set))}")
        if texts_set:
            lines.append(f"  Text objects: {', '.join(sorted(texts_set))}")

        # Object positions
        lines.append("\nKey positions:")

        # Find YOU positions
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in [o.lower() for o in you_objects]:
                        lines.append(f"  {obj.name} (YOU) at ({x},{y})")

        # Find WIN positions
        for y in range(grid.height):
            for x in range(grid.width):
                for obj in grid.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in [o.lower() for o in win_objects]:
                        lines.append(f"  {obj.name} (WIN) at ({x},{y})")

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
