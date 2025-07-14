"""
Agent interface for Baba Is You.

This provides the base Agent class that can be used for creating
agents that work with EpisodePlayer.
"""

from abc import ABC, abstractmethod

import pygame

from .grid import Grid


class Agent(ABC):
    """
    Abstract base class for all Baba Is You agents.

    Agents decide which action to take given the current game state.
    """

    def __init__(self, name: str = "Agent"):
        """
        Initialize the agent.

        Args:
            name: Display name for this agent
        """
        self.name = name

    @abstractmethod
    def get_action(self, grid: Grid) -> str | None:
        """
        Choose an action given the current game state.

        Args:
            grid: Current game grid

        Returns:
            Action string ("up", "down", "left", "right", "wait") or None to quit
        """
        pass

    def reset(self):  # noqa: B027
        """
        Reset the agent for a new episode.

        Override this if your agent maintains internal state.
        """
        pass  # Default implementation does nothing


class UserAgent(Agent):
    """
    Human player agent that gets actions from keyboard input.

    Controls:
    - Arrow keys or WASD: Movement
    - Space: Wait
    - R: Reset level (returns special action)
    - Q/ESC: Quit
    """

    def __init__(self):
        super().__init__("Human Player")
        self._quit_requested = False
        self._reset_requested = False

    def get_action(self, grid: Grid) -> str | None:  # noqa: ARG002
        """
        Get action from keyboard input.

        Returns:
            Action string or None to quit
        """
        # Handle any pending requests
        if self._quit_requested:
            return None
        if self._reset_requested:
            self._reset_requested = False
            return "reset"

        # Wait for keyboard input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_requested = True
                    return None

                elif event.type == pygame.KEYDOWN:
                    # Movement keys
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        return "up"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        return "down"
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        return "left"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        return "right"
                    elif event.key == pygame.K_SPACE:
                        return "wait"

                    # Control keys
                    elif event.key == pygame.K_r:
                        self._reset_requested = True
                        return "reset"
                    elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        self._quit_requested = True
                        return None

            # Small delay to prevent high CPU usage
            pygame.time.wait(10)
