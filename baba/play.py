"""Interactive gameplay with pygame for Baba Is You."""

import sys
from typing import Optional

try:
    import pygame
except ImportError:
    print("pygame not found. Please install it with: pip install pygame")
    sys.exit(1)

from .envs import create_environment, list_environments
from .grid import Grid


class GamePlayer:
    """Interactive game player using pygame."""

    def __init__(self, env_name: str = "simple", cell_size: int = 48):
        """
        Initialize the game player.

        Args:
            env_name: Name of the environment to play
            cell_size: Size of each cell in pixels
        """
        self.env = create_environment(env_name)
        if not self.env:
            print(f"Environment '{env_name}' not found.")
            print(f"Available environments: {', '.join(list_environments())}")
            sys.exit(1)
        
        self.cell_size = cell_size
        self.running = True
        self.clock = None
        self.screen = None
        self.font = None
        
        # Initialize pygame
        pygame.init()
        self.setup_display()

    def setup_display(self):
        """Set up the pygame display."""
        width = self.env.width * self.cell_size
        height = self.env.height * self.cell_size + 100  # Extra space for UI
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Baba Is You - {self.env.name}")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

    def render(self):
        """Render the game state."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render the grid
        grid_surface = pygame.surfarray.make_surface(
            self.env.render(self.cell_size).swapaxes(0, 1)
        )
        self.screen.blit(grid_surface, (0, 0))
        
        # Render UI elements
        self.render_ui()
        
        # Update display
        pygame.display.flip()

    def render_ui(self):
        """Render UI elements like status and controls."""
        y_offset = self.env.height * self.cell_size + 10
        
        # Game status
        if self.env.grid.won:
            status_text = "YOU WIN! Press R to restart"
            color = (0, 255, 0)
        elif self.env.grid.lost:
            status_text = "YOU LOSE! Press R to restart"
            color = (255, 0, 0)
        else:
            status_text = f"Steps: {self.env.grid.steps}"
            color = (255, 255, 255)
        
        status_surface = self.font.render(status_text, True, color)
        self.screen.blit(status_surface, (10, y_offset))
        
        # Controls
        controls = [
            "Arrow Keys: Move",
            "R: Restart",
            "ESC: Quit"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, (200, 200, 200))
            self.screen.blit(control_surface, (10, y_offset + 30 + i * 20))
        
        # Active rules
        rules_text = "Rules: " + ", ".join(str(rule) for rule in self.env.grid.rule_manager.rules[:3])
        if len(self.env.grid.rule_manager.rules) > 3:
            rules_text += "..."
        
        rules_surface = self.font.render(rules_text, True, (150, 150, 255))
        self.screen.blit(rules_surface, (self.env.width * self.cell_size - 300, y_offset))

    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_r:
                    # Restart
                    self.env.reset()
                
                elif not self.env.grid.won and not self.env.grid.lost:
                    # Movement
                    if event.key == pygame.K_UP:
                        self.env.step("up")
                    elif event.key == pygame.K_DOWN:
                        self.env.step("down")
                    elif event.key == pygame.K_LEFT:
                        self.env.step("left")
                    elif event.key == pygame.K_RIGHT:
                        self.env.step("right")
                    elif event.key == pygame.K_SPACE:
                        self.env.step("wait")

    def run(self):
        """Run the game loop."""
        while self.running:
            # Handle input
            self.handle_input()
            
            # Render
            self.render()
            
            # Control frame rate
            self.clock.tick(30)
        
        # Cleanup
        pygame.quit()


def main():
    """Main entry point for playing the game."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Play Baba Is You")
    parser.add_argument(
        "--env",
        default="simple",
        choices=list_environments(),
        help="Environment to play"
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=48,
        help="Size of each cell in pixels"
    )
    
    args = parser.parse_args()
    
    # Create and run the game
    player = GamePlayer(args.env, args.cell_size)
    player.run()


if __name__ == "__main__":
    main()