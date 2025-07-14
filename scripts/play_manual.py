#!/usr/bin/env python3
"""
Play Baba Is You manually with keyboard controls.
"""
import pygame
from baba import make
from baba.envs import list_environments
import sys

def main():
    # Get list of available environments
    available_envs = list_environments()
    
    # Default to first available environment
    env_name = available_envs[0] if available_envs else "simple"
    
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if env_name not in available_envs:
            print(f"Environment '{env_name}' not found.")
            print(f"Available environments: {', '.join(available_envs)}")
            return
    
    print(f"🎮 Manual play: {env_name}")
    print("Controls:")
    print("  Arrow keys or WASD: Move")
    print("  R: Reset level")
    print("  ESC: Quit")
    print()
    
    # Create environment
    env = make(env_name)
    env.reset()
    
    # Initialize pygame
    pygame.init()
    cell_size = 48
    width = env.width * cell_size
    height = env.height * cell_size
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Baba Is You - {env_name}")
    clock = pygame.time.Clock()
    
    # Game loop
    running = True
    game_over = False
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    env.reset()
                    game_over = False
                    print("Level reset!")
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if not game_over:
                        _, won, lost = env.step("up")
                        if won:
                            print("🎉 You won!")
                            game_over = True
                        elif lost:
                            print("💀 You lost!")
                            game_over = True
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if not game_over:
                        _, won, lost = env.step("down")
                        if won:
                            print("🎉 You won!")
                            game_over = True
                        elif lost:
                            print("💀 You lost!")
                            game_over = True
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    if not game_over:
                        _, won, lost = env.step("left")
                        if won:
                            print("🎉 You won!")
                            game_over = True
                        elif lost:
                            print("💀 You lost!")
                            game_over = True
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    if not game_over:
                        _, won, lost = env.step("right")
                        if won:
                            print("🎉 You won!")
                            game_over = True
                        elif lost:
                            print("💀 You lost!")
                            game_over = True
        
        # Render
        grid_image = env.render(cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        screen.blit(grid_surface, (0, 0))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()