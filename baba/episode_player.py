"""
Episode player for running Baba Is You games with any agent.

This module provides a unified way to play episodes, whether with
human input, AI agents, or any other agent implementation.
"""

from pathlib import Path

import pygame
from PIL import Image

from .agent import Agent
from .envs import Environment


class EpisodePlayer:
    """
    Plays episodes of Baba Is You with any agent.

    Handles:
    - Game loop execution
    - Rendering (optional)
    - Episode statistics
    - Win/lose detection
    - Recording gameplay to GIF (optional)
    """

    def __init__(
        self,
        env: Environment,
        agent: Agent,
        render: bool = True,
        cell_size: int = 48,
        fps: int = 30,
        verbose: bool = True,
        record: bool = False,
        record_path: str | None = None,
    ):
        """
        Initialize episode player.

        Args:
            env: Environment to play in
            agent: Agent that will provide actions
            render: Whether to render the game visually
            cell_size: Size of each cell in pixels (if rendering)
            fps: Frames per second (if rendering)
            verbose: Whether to print episode information
            record: Whether to record episodes as GIF
            record_path: Path for saving recordings (auto-generated if None)
        """
        self.env = env
        self.agent = agent
        self.render_enabled = render
        self.cell_size = cell_size
        self.fps = fps
        self.verbose = verbose
        self.record_enabled = record
        self.record_path = record_path

        # Recording state
        self.frames: list[Image.Image] = []
        self.recording_episode = False

        # Pygame setup (only if rendering)
        self.screen = None
        self.clock = None
        self.font = None
        if self.render_enabled:
            self._setup_pygame()

    def _setup_pygame(self):
        """Initialize pygame for rendering."""
        pygame.init()

        width = self.env.width * self.cell_size
        height = self.env.height * self.cell_size + 100  # Extra space for UI

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Baba Is You - {self.env.name} ({self.agent.name})")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

    def play_episode(self) -> tuple[bool, bool, int]:
        """
        Play a single episode.

        Returns:
            Tuple of (won, lost, steps)
        """
        # Reset environment and agent
        grid = self.env.reset()
        self.agent.reset()

        # Start recording if enabled
        if self.record_enabled and self.render_enabled:
            self.frames = []
            self.recording_episode = True
            # Capture initial state
            self._render()
            self._capture_frame()

        if self.verbose:
            print(f"\n=== Starting Episode: {self.env.name} with {self.agent.name} ===")

        # Episode loop
        while True:
            # Render if enabled
            if self.render_enabled:
                self._render()
                if self.recording_episode:
                    self._capture_frame()
                self.clock.tick(self.fps)

            # Get action from agent
            action = self.agent.get_action(grid)

            # Handle special actions
            if action is None:
                # Agent wants to quit
                if self.verbose:
                    print("Agent requested quit")
                return grid.won, grid.lost, grid.steps

            elif action == "reset":
                # Reset the environment
                if self.verbose:
                    print("Resetting environment")
                grid = self.env.reset()
                continue

            # Take action in environment
            grid, won, lost = self.env.step(action)

            if self.verbose and (won or lost):
                if won:
                    print(f"🎉 Won in {grid.steps} steps!")
                else:
                    print(f"💀 Lost after {grid.steps} steps")

            # Check if episode is done
            if won or lost:
                # Show final state briefly
                if self.render_enabled:
                    self._render()
                    pygame.time.wait(1000)

                # Save final frames if recording
                if self.recording_episode:
                    for _ in range(5):  # Capture final state
                        self._render()
                        self._capture_frame()
                    self._save_recording()

                return won, lost, grid.steps

    def _render(self):
        """Render the current game state."""
        if not self.screen:
            return

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Render the grid
        grid_image = self.env.render(self.cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        self.screen.blit(grid_surface, (0, 0))

        # Render UI
        self._render_ui()

        # Update display
        pygame.display.flip()

    def _render_ui(self):
        """Render UI elements."""
        grid = self.env.grid
        y_offset = self.env.height * self.cell_size + 10

        # Status text
        if grid.won:
            status_text = "YOU WIN!"
            color = (0, 255, 0)
        elif grid.lost:
            status_text = "YOU LOSE!"
            color = (255, 0, 0)
        else:
            status_text = f"Steps: {grid.steps}"
            color = (255, 255, 255)

        # Add agent name
        status_text += f" | Agent: {self.agent.name}"

        status_surface = self.font.render(status_text, True, color)
        self.screen.blit(status_surface, (10, y_offset))

        # Active rules (show first few)
        rules = grid.rule_manager.rules[:4]
        if rules:
            rules_text = "Rules: " + ", ".join(str(rule) for rule in rules)
            if len(grid.rule_manager.rules) > 4:
                rules_text += f" (+{len(grid.rule_manager.rules) - 4} more)"

            rules_surface = self.font.render(rules_text, True, (150, 150, 255))
            self.screen.blit(rules_surface, (10, y_offset + 30))

        # Controls (for UserAgent)
        if hasattr(self.agent, "get_action") and self.agent.__class__.__name__ == "UserAgent":
            controls = "Controls: ↑↓←→/WASD=Move, Space=Wait, R=Reset, Q/ESC=Quit"
            control_surface = self.font.render(controls, True, (200, 200, 200))
            self.screen.blit(control_surface, (10, y_offset + 60))

    def play_episodes(self, num_episodes: int = 1) -> dict:
        """
        Play multiple episodes and return statistics.

        Args:
            num_episodes: Number of episodes to play

        Returns:
            Dictionary with statistics
        """
        stats = {
            "episodes": num_episodes,
            "wins": 0,
            "losses": 0,
            "total_steps": 0,
            "win_steps": [],
            "loss_steps": [],
        }

        try:
            for episode in range(num_episodes):
                if self.verbose and num_episodes > 1:
                    print(f"\n--- Episode {episode + 1}/{num_episodes} ---")

                won, lost, steps = self.play_episode()

                stats["total_steps"] += steps
                if won:
                    stats["wins"] += 1
                    stats["win_steps"].append(steps)
                elif lost:
                    stats["losses"] += 1
                    stats["loss_steps"].append(steps)

                # Check if we should continue
                if hasattr(self.agent, "_quit_requested") and self.agent._quit_requested:
                    break

        finally:
            # Cleanup pygame if it was initialized
            if self.render_enabled and pygame.get_init():
                pygame.quit()

        # Print summary for multiple episodes
        if self.verbose and num_episodes > 1:
            print("\n=== Episode Summary ===")
            print(f"Total episodes: {episode + 1}")
            print(f"Wins: {stats['wins']} ({stats['wins'] / (episode + 1) * 100:.1f}%)")
            print(f"Losses: {stats['losses']} ({stats['losses'] / (episode + 1) * 100:.1f}%)")
            if stats["win_steps"]:
                print(f"Average win steps: {sum(stats['win_steps']) / len(stats['win_steps']):.1f}")

        return stats

    def _capture_frame(self):
        """Capture current screen as a frame for recording."""
        if not self.screen or not self.recording_episode:
            return

        # Convert pygame surface to PIL Image
        frame_str = pygame.image.tostring(self.screen, "RGB")
        width, height = self.screen.get_size()
        frame = Image.frombytes("RGB", (width, height), frame_str)
        self.frames.append(frame)

    def _save_recording(self, custom_path: str | None = None):
        """Save recorded frames as GIF."""
        if not self.frames:
            return

        # Determine output path
        if custom_path:
            output_path = custom_path
        elif self.record_path:
            output_path = self.record_path
        else:
            # Auto-generate filename
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = (
                f"recordings/{self.env.name}_{self.agent.name.replace(' ', '_')}_{timestamp}.gif"
            )

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save GIF
        if self.verbose:
            print(f"Saving recording to {output_path}...")

        # Calculate frame duration based on FPS
        duration_ms = int(1000 / self.fps)

        self.frames[0].save(
            output_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

        if self.verbose:
            print(
                f"Recording saved! {len(self.frames)} frames, {Path(output_path).stat().st_size / 1024:.1f} KB"
            )

        # Clear frames
        self.frames = []
        self.recording_episode = False

        return output_path
