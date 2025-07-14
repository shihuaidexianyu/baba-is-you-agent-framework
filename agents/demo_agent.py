#!/usr/bin/env python3
"""
Simple demo agent for Baba Is You that can solve basic levels.
Uses BFS pathfinding to reach WIN objects, handling pushable objects.
"""

from collections import deque

from baba.agent import Agent
from baba.grid import Grid


class DemoAgent(Agent):
    """Agent that uses BFS pathfinding to reach WIN objects."""

    def __init__(self):
        super().__init__("Demo Agent")
        self.path_cache = {}  # Cache paths between episodes
        self.last_reasoning = ""  # Empty for UI consistency (demo agent doesn't "think")

    def reset(self):
        """Reset the agent for a new episode."""
        self.path_cache = {}
        self.last_reasoning = ""  # Empty for UI consistency

    def get_action(self, observation: Grid) -> str:
        """
        Choose action using simplified pathfinding that handles pushable objects.

        Args:
            observation: Current game state

        Returns:
            Action to take
        """
        # Find YOU and WIN objects
        you_objects = observation.rule_manager.get_you_objects()
        win_objects = observation.rule_manager.get_win_objects()

        if not you_objects:
            return "wait"  # No controllable objects

        # Get current positions
        you_positions = self._find_you_positions(observation, you_objects)
        win_positions = self._find_win_positions(observation, win_objects)

        if not you_positions or not win_positions:
            return "wait"  # Can't find positions

        # For simplicity, control the first YOU object
        you_pos = you_positions[0]
        target_pos = win_positions[0]

        # Try simple pathfinding with push awareness
        action = self._simple_pathfind_with_push(observation, you_pos, target_pos)

        # Keep reasoning empty - demo agent doesn't "think"
        self.last_reasoning = ""

        return action

    def _find_you_positions(self, observation: Grid, you_objects: set[str]) -> list:
        """Find all positions of controllable objects."""
        positions = []
        # Convert to lowercase for comparison
        you_objects_lower = {obj.lower() for obj in you_objects}
        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in you_objects_lower:
                        positions.append((x, y))
        return positions

    def _find_win_positions(self, observation: Grid, win_objects: set[str]) -> list:
        """Find all positions of win objects."""
        positions = []
        # Convert to lowercase for comparison
        win_objects_lower = {obj.lower() for obj in win_objects}
        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in win_objects_lower:
                        positions.append((x, y))
        return positions

    def _get_push_positions(self, observation: Grid) -> set[tuple[int, int]]:
        """Get positions of all pushable objects."""
        push_objects = observation.rule_manager.get_push_objects()
        # Convert to lowercase for comparison
        push_objects_lower = {obj.lower() for obj in push_objects}
        positions = set()

        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in push_objects_lower:
                        positions.add((x, y))

        return positions

    def _simple_pathfind_with_push(
        self, observation: Grid, start: tuple[int, int], goal: tuple[int, int]
    ) -> str:
        """
        Simplified pathfinding that tries to reach goal, pushing objects if needed.
        Uses local BFS to find immediate next move.
        """
        # Get object types (convert to lowercase for comparison)
        push_objects = {obj.lower() for obj in observation.rule_manager.get_push_objects()}
        stop_objects = {obj.lower() for obj in observation.rule_manager.get_stop_objects()}

        # BFS for immediate area (depth limited)
        queue = deque([(start, [], 0)])
        visited = {start}
        max_local_depth = 10  # Look ahead a few moves

        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

        while queue:
            pos, path, depth = queue.popleft()

            if depth > max_local_depth:
                continue

            # Check if we reached goal
            if pos == goal:
                return path[0] if path else "wait"

            # Try each direction
            for action, (dx, dy) in directions.items():
                new_x = pos[0] + dx
                new_y = pos[1] + dy

                # Check bounds
                if (
                    new_x < 0
                    or new_x >= observation.width
                    or new_y < 0
                    or new_y >= observation.height
                ):
                    continue

                # Check what's at the new position
                can_move = True

                for obj in observation.grid[new_y][new_x]:
                    if obj.is_text:
                        continue

                    # Check if it's a stop object
                    if obj.name in stop_objects:
                        # Check if it's also pushable
                        if obj.name in push_objects:
                            # Check if we can push it
                            push_x = new_x + dx
                            push_y = new_y + dy

                            # Check push bounds
                            if (
                                push_x < 0
                                or push_x >= observation.width
                                or push_y < 0
                                or push_y >= observation.height
                            ):
                                can_move = False
                                break

                            # Check if push destination is blocked
                            for push_obj in observation.grid[push_y][push_x]:
                                if not push_obj.is_text and push_obj.name in stop_objects:
                                    can_move = False
                                    break
                        else:
                            # It's STOP but not PUSH
                            can_move = False
                            break

                if can_move and (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append(((new_x, new_y), path + [action], depth + 1))

        # If no path found with BFS, try direct greedy approach
        return self._greedy_move_with_push(observation, start, goal)

    def _greedy_move_with_push(
        self, observation: Grid, you_pos: tuple[int, int], goal_pos: tuple[int, int]
    ) -> str:
        """Greedy movement that considers if we can push objects."""
        you_x, you_y = you_pos
        goal_x, goal_y = goal_pos

        # Determine preferred direction
        dx = goal_x - you_x
        dy = goal_y - you_y

        # Try horizontal first if it's the longer distance
        if abs(dx) >= abs(dy):
            if dx > 0:
                action = "right"
            elif dx < 0:
                action = "left"
            elif dy > 0:
                action = "down"
            elif dy < 0:
                action = "up"
            else:
                return "wait"
        else:
            if dy > 0:
                action = "down"
            elif dy < 0:
                action = "up"
            elif dx > 0:
                action = "right"
            elif dx < 0:
                action = "left"
            else:
                return "wait"

        # Check if this move is valid
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = directions[action]
        new_x = you_x + dx
        new_y = you_y + dy

        # Bounds check
        if new_x < 0 or new_x >= observation.width or new_y < 0 or new_y >= observation.height:
            return "wait"

        # Check if move is valid (considering pushing)
        push_objects = {obj.lower() for obj in observation.rule_manager.get_push_objects()}
        stop_objects = {obj.lower() for obj in observation.rule_manager.get_stop_objects()}

        for obj in observation.grid[new_y][new_x]:
            if obj.is_text:
                continue

            if obj.name in stop_objects:
                if obj.name in push_objects:
                    # Can push - check if push is valid
                    push_x = new_x + dx
                    push_y = new_y + dy

                    if (
                        push_x < 0
                        or push_x >= observation.width
                        or push_y < 0
                        or push_y >= observation.height
                    ):
                        return "wait"

                    # Check push destination
                    for push_obj in observation.grid[push_y][push_x]:
                        if not push_obj.is_text and push_obj.name in stop_objects:
                            return "wait"
                else:
                    # Can't push, blocked
                    return "wait"

        return action


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
    agent = DemoAgent()
    stats = agent.play_episode(env, render=True, verbose=True)

    print(f"\nFinal stats: {stats}")
