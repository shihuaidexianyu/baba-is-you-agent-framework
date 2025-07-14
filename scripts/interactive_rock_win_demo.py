#!/usr/bin/env python3
"""Create a custom level to test ROCK IS WIN properly."""

from baba.registration import Registry
from baba.grid import Grid
import pygame

# Initialize pygame
pygame.init()

# Create registry and grid
registry = Registry()
grid = Grid(15, 10, registry)

# Place BABA IS YOU in a row
grid.place_object(registry.create_instance("baba", is_text=True), 1, 1)
grid.place_object(registry.create_instance("is", is_text=True), 2, 1)
grid.place_object(registry.create_instance("you", is_text=True), 3, 1)

# Place ROCK IS WIN in a row (properly aligned)
grid.place_object(registry.create_instance("rock", is_text=True), 1, 3)
grid.place_object(registry.create_instance("is", is_text=True), 2, 3)
grid.place_object(registry.create_instance("win", is_text=True), 3, 3)

# Place actual Baba and Rock objects
grid.place_object(registry.create_instance("baba", is_text=False), 5, 5)
grid.place_object(registry.create_instance("rock", is_text=False), 7, 5)

# Place some walls
for x in range(10):
    grid.place_object(registry.create_instance("wall", is_text=False), x, 7)

# Update rules
grid._update_rules()

print("Active rules:")
for rule in grid.rule_manager.rules:
    print(f"  {rule}")

print("\nWIN objects:", grid.rule_manager.get_win_objects())
print("YOU objects:", grid.rule_manager.get_you_objects())

# Create display
cell_size = 48
width = grid.width * cell_size
height = grid.height * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Test ROCK IS WIN")
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                grid.step("up")
            elif event.key == pygame.K_DOWN:
                grid.step("down")
            elif event.key == pygame.K_LEFT:
                grid.step("left")
            elif event.key == pygame.K_RIGHT:
                grid.step("right")
            
            # Check win
            if grid.won:
                print("YOU WON!")
                running = False
    
    # Render
    screen.fill((30, 30, 30))
    
    # Render all objects
    for y in range(grid.height):
        for x in range(grid.width):
            for obj in grid.grid[y][x]:
                # Simple colored rectangles for now
                color = getattr(obj, 'color', (128, 128, 128))
                if isinstance(color, tuple) and len(color) == 3:
                    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                    
                    # Draw text for text objects
                    if obj.is_text and hasattr(obj, 'text'):
                        font = pygame.font.Font(None, 20)
                        text = font.render(obj.text, True, (255, 255, 255))
                        text_rect = text.get_rect(center=(x * cell_size + cell_size // 2, 
                                                         y * cell_size + cell_size // 2))
                        screen.blit(text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()