"""
Agent interface for Baba Is You with built-in episode playing functionality.

Agents only need to implement get_action(observation) to work.
The base class provides play_episode() and play_episodes() methods for convenience.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pygame
from PIL import Image

from .grid import Grid


class Agent(ABC):
    """
    Abstract base class for Baba Is You agents.

    Subclasses only need to implement get_action(observation).
    The base class provides convenient methods for playing episodes.
    """

    def __init__(self, name: str = "Agent"):
        """Initialize the agent with a name."""
        self.name = name

    @abstractmethod
    def get_action(self, observation: Grid) -> str:
        """
        Choose an action given the current observation.

        Args:
            observation: Current game state (Grid object)

        Returns:
            Action string: one of ["up", "down", "left", "right", "wait"]
        """
        pass

    def reset(self):  # noqa: B027
        """
        Reset the agent for a new episode.

        Override this if your agent maintains internal state.
        """
        pass

    def play_episode(
        self,
        env,
        render: bool = False,
        record: bool = False,
        record_path: str | None = None,
        cell_size: int = 48,
        fps: int = 30,
        verbose: bool = True,
        max_steps: int = 200,
    ) -> dict:
        """
        Play a single episode in the environment.

        Args:
            env: Environment to play in
            render: Whether to render the game visually
            record: Whether to record the episode as a GIF
            record_path: Path to save recording (auto-generated if None)
            cell_size: Size of each cell in pixels when rendering
            fps: Frames per second for rendering
            verbose: Whether to print episode information
            max_steps: Maximum steps before forcing episode to end

        Returns:
            Dictionary with episode statistics
        """
        # Initialize pygame if rendering
        screen = None
        clock = None
        font = None
        frames = []

        if render:
            pygame.init()
            width = env.width * cell_size
            height = env.height * cell_size + 120  # Extra space for UI with reasoning
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(f"Baba Is You - {env.name} ({self.name})")
            clock = pygame.time.Clock()
            font = pygame.font.Font(None, 24)

        # Reset environment and agent
        obs = env.reset()
        self.reset()

        if verbose:
            print(f"\n=== Playing {env.name} with {self.name} ===")

        # Episode loop
        done = False
        total_reward = 0.0
        steps = 0
        start_time = pygame.time.get_ticks() if render else 0

        while not done and steps < max_steps:
            # Render if enabled
            if render:
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
                self._render_frame(screen, env, obs, font, cell_size, elapsed_time)
                if record:
                    frames.append(self._capture_frame(screen))
                clock.tick(fps)

                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        break

            # Get action from agent
            action = self.get_action(obs)

            # Take action in environment
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1

            if verbose and done:
                if info["won"]:
                    print(f"🎉 Won in {info['steps']} steps!")
                elif info["lost"]:
                    print(f"💀 Lost after {info['steps']} steps")

            # Check if we hit the step limit
            if steps >= max_steps and not done:
                done = True
                info["timeout"] = True
                if verbose:
                    print(f"⏱️ Timeout after {max_steps} steps")

        # Save recording if enabled
        if record and frames:
            self._save_recording(frames, record_path, env, fps, verbose)

        # Cleanup pygame
        if render:
            pygame.quit()

        # Return episode statistics
        return {
            "won": info.get("won", False),
            "lost": info.get("lost", False),
            "steps": info.get("steps", steps),
            "reward": total_reward,
            "timeout": info.get("timeout", False),
        }

    def play_episodes(
        self, env, num_episodes: int = 1, render: bool = False, verbose: bool = True, **kwargs
    ) -> dict:
        """
        Play multiple episodes and return aggregated statistics.

        Args:
            env: Environment to play in
            num_episodes: Number of episodes to play
            render: Whether to render the game visually
            verbose: Whether to print episode information
            **kwargs: Additional arguments passed to play_episode()

        Returns:
            Dictionary with aggregated statistics
        """
        stats = {
            "episodes": num_episodes,
            "wins": 0,
            "losses": 0,
            "total_steps": 0,
            "total_reward": 0.0,
            "win_rate": 0.0,
            "avg_steps": 0.0,
            "avg_reward": 0.0,
        }

        for i in range(num_episodes):
            if verbose and num_episodes > 1:
                print(f"\n--- Episode {i + 1}/{num_episodes} ---")

            episode_stats = self.play_episode(env, render=render, verbose=verbose, **kwargs)

            # Update statistics
            if episode_stats["won"]:
                stats["wins"] += 1
            elif episode_stats["lost"]:
                stats["losses"] += 1
            stats["total_steps"] += episode_stats["steps"]
            stats["total_reward"] += episode_stats["reward"]

        # Calculate averages
        stats["win_rate"] = stats["wins"] / num_episodes if num_episodes > 0 else 0.0
        stats["avg_steps"] = stats["total_steps"] / num_episodes if num_episodes > 0 else 0.0
        stats["avg_reward"] = stats["total_reward"] / num_episodes if num_episodes > 0 else 0.0

        # Print summary
        if verbose and num_episodes > 1:
            print("\n=== Episode Summary ===")
            print(f"Total episodes: {num_episodes}")
            print(f"Wins: {stats['wins']} ({stats['win_rate']*100:.1f}%)")
            print(f"Losses: {stats['losses']}")
            print(f"Average steps: {stats['avg_steps']:.1f}")
            print(f"Average reward: {stats['avg_reward']:.2f}")

        return stats

    def _render_frame(
        self, screen, env, obs: Grid, font, cell_size: int, elapsed_time: float = 0.0
    ):
        """Render a single frame."""
        # Clear screen
        screen.fill((0, 0, 0))

        # Render the grid
        grid_image = env.render("rgb_array", cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        screen.blit(grid_surface, (0, 0))

        # Render UI
        y_offset = env.height * cell_size + 10

        # Status text
        if obs.won:
            status_text = "YOU WIN!"
            color = (0, 255, 0)
        elif obs.lost:
            status_text = "YOU LOSE!"
            color = (255, 0, 0)
        else:
            status_text = f"Steps: {obs.steps} | Time: {elapsed_time:.1f}s"
            color = (255, 255, 255)

        status_text += f" | Agent: {self.name}"
        status_surface = font.render(status_text, True, color)
        screen.blit(status_surface, (10, y_offset))

        # Show agent reasoning if available
        if hasattr(self, "last_reasoning"):
            reasoning_text = f"Thinking: {self.last_reasoning}"
            reasoning_surface = font.render(reasoning_text, True, (255, 255, 100))
            screen.blit(reasoning_surface, (10, y_offset + 25))
            rules_y_offset = y_offset + 50
        else:
            rules_y_offset = y_offset + 30

        # Rules (show first few)
        rules = obs.rule_manager.rules[:4]
        if rules:
            rules_text = "Rules: " + ", ".join(str(rule) for rule in rules)
            if len(obs.rule_manager.rules) > 4:
                rules_text += f" (+{len(obs.rule_manager.rules) - 4} more)"
            rules_surface = font.render(rules_text, True, (150, 150, 255))
            screen.blit(rules_surface, (10, rules_y_offset))

        pygame.display.flip()

    def _capture_frame(self, screen) -> Image.Image:
        """Capture current screen as PIL Image."""
        frame_str = pygame.image.tostring(screen, "RGB")
        width, height = screen.get_size()
        return Image.frombytes("RGB", (width, height), frame_str)

    def _save_recording(self, frames: list, record_path: str | None, env, fps: int, verbose: bool):
        """Save frames as animated GIF."""
        if not frames:
            return

        # Determine output path
        if record_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            record_path = f"recordings/{env.name}_{self.name.replace(' ', '_')}_{timestamp}.gif"

        # Ensure directory exists
        Path(record_path).parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Saving recording to {record_path}...")

        # Save GIF
        duration_ms = int(1000 / fps)
        frames[0].save(
            record_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

        if verbose:
            size_kb = Path(record_path).stat().st_size / 1024
            print(f"Recording saved! {len(frames)} frames, {size_kb:.1f} KB")


class UserAgent(Agent):
    """
    Human player agent that gets actions from keyboard input.

    Controls:
    - Arrow keys or WASD: Movement
    - Space: Wait
    - Q/ESC: Quit (handled by play_episode)
    """

    def __init__(self):
        super().__init__("Human Player")

    def get_action(self, observation: Grid) -> str:  # noqa: ARG002
        """
        Get action from keyboard input.

        Returns:
            Action string
        """
        # Wait for keyboard input
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
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

            # Small delay to prevent high CPU usage
            pygame.time.wait(10)
