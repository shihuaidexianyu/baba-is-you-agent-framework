#!/usr/bin/env python3
"""Visualize an official Baba Is You level with pygame."""

import sys
import pygame
from baba.level_loader import LevelLoader
from baba.registration import Registry


def visualize_level(world="baba", level_num=3):
    """Load and visualize a level with pygame."""
    # Create registry
    registry = Registry()
    
    # Initialize level loader
    loader = LevelLoader()
    
    print(f"Loading level {level_num} from world '{world}'...")
    
    # Load the level
    grid = loader.load_level(world, level_num, registry)
    
    if not grid:
        print("Failed to load level!")
        return
        
    print(f"Level {level_num} loaded - Size: {grid.width}x{grid.height}")
    
    # Count objects
    object_count = {}
    object_positions = {}
    
    for y in range(grid.height):
        for x in range(grid.width):
            for obj in grid.grid[y][x]:
                obj_type = obj.name
                object_count[obj_type] = object_count.get(obj_type, 0) + 1
                if obj_type not in object_positions:
                    object_positions[obj_type] = []
                object_positions[obj_type].append((x, y))
    
    print("\nObjects found:")
    for obj_type, count in sorted(object_count.items()):
        print(f"  {obj_type}: {count}")
        # Show first few positions
        positions = object_positions[obj_type][:3]
        pos_str = ", ".join([f"({x},{y})" for x, y in positions])
        if len(object_positions[obj_type]) > 3:
            pos_str += "..."
        print(f"    at: {pos_str}")
    
    # Initialize pygame
    pygame.init()
    
    cell_size = 48
    width = grid.width * cell_size
    height = grid.height * cell_size + 100  # Extra space for info
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Baba Is You - Level {level_num}")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT and level_num > 0:
                    pygame.quit()
                    return visualize_level(world, level_num - 1)
                elif event.key == pygame.K_RIGHT:
                    pygame.quit()
                    return visualize_level(world, level_num + 1)
        
        # Clear screen
        screen.fill((20, 20, 20))
        
        # Render the grid
        try:
            surface = grid.render(cell_size)
            screen.blit(surface, (0, 0))
        except Exception as e:
            # If rendering fails, draw a simple representation
            for y in range(grid.height):
                for x in range(grid.width):
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    if grid.grid[y][x]:
                        pygame.draw.rect(screen, (100, 100, 100), rect)
                    pygame.draw.rect(screen, (50, 50, 50), rect, 1)
        
        # Draw info panel
        info_y = grid.height * cell_size + 10
        info_text = f"Level {level_num} | Objects: {sum(object_count.values())} | Press ← → to navigate levels"
        text = font.render(info_text, True, (255, 255, 255))
        screen.blit(text, (10, info_y))
        
        # Show object types
        obj_text = "Objects: " + ", ".join([f"{k}({v})" for k, v in object_count.items()][:5])
        if len(object_count) > 5:
            obj_text += "..."
        text = font.render(obj_text, True, (200, 200, 200))
        screen.blit(text, (10, info_y + 30))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()


def main():
    world = "baba"
    level_num = 0
    
    if len(sys.argv) > 1:
        level_num = int(sys.argv[1])
    if len(sys.argv) > 2:
        world = sys.argv[2]
    
    print("Controls:")
    print("  ← → : Navigate between levels")
    print("  ESC : Quit")
    print()
    
    visualize_level(world, level_num)


if __name__ == "__main__":
    main()