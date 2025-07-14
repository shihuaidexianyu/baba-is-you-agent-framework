#!/usr/bin/env python3
"""
User-controlled agent for Baba Is You.
"""

import pygame

from baba import create_environment


def main():
    """Play Baba Is You with keyboard controls."""
    import sys

    # Get environment from command line or use default
    env_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        return

    # Initialize pygame
    pygame.init()

    # Set up display
    cell_size = 48
    width = env.width * cell_size
    height = env.height * cell_size + 100  # Extra space for UI

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Baba Is You - {env_name}")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Reset to get initial state
    grid = env.reset()

    print(f"Playing {env_name}")
    print("Controls: Arrow keys/WASD to move, R to reset, Q to quit")

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = None

                # Movement
                if event.key in [pygame.K_UP, pygame.K_w]:
                    action = "up"
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    action = "down"
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    action = "left"
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    action = "right"
                elif event.key == pygame.K_SPACE:
                    action = "wait"

                # Control
                elif event.key == pygame.K_r:
                    grid = env.reset()
                    print("Reset")
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    running = False

                # Take action if any
                if action and running:
                    grid, won, lost = env.step(action)

                    if won:
                        print(f"✅ Won in {grid.steps} steps!")
                        pygame.time.wait(2000)
                        running = False
                    elif lost:
                        print(f"❌ Lost after {grid.steps} steps")
                        pygame.time.wait(2000)
                        running = False

        # Render
        screen.fill((0, 0, 0))

        # Render grid
        grid_image = env.render(cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        screen.blit(grid_surface, (0, 0))

        # Render UI
        y_offset = env.height * cell_size + 10

        # Status
        status = f"Steps: {grid.steps}"
        if grid.won:
            status = "YOU WIN!"
            color = (0, 255, 0)
        elif grid.lost:
            status = "YOU LOSE!"
            color = (255, 0, 0)
        else:
            color = (255, 255, 255)

        status_surface = font.render(status, True, color)
        screen.blit(status_surface, (10, y_offset))

        # Rules
        rules = grid.rule_manager.rules[:3]
        if rules:
            rules_text = "Rules: " + ", ".join(str(r) for r in rules)
            if len(grid.rule_manager.rules) > 3:
                rules_text += f" (+{len(grid.rule_manager.rules) - 3})"
            rules_surface = font.render(rules_text, True, (150, 150, 255))
            screen.blit(rules_surface, (10, y_offset + 30))

        # Update display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
