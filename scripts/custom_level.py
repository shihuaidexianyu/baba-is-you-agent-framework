#!/usr/bin/env python3
"""
Example of creating a custom Baba Is You level.
"""

from baba.grid import Grid
from baba.world_object import Object, TextObject
from baba.registration import Registry
from baba import play

def create_custom_level():
    """Create a custom level with specific rules and objects."""
    # Initialize a 10x10 grid
    grid = Grid(width=10, height=10)
    registry = Registry()
    
    # Register game objects
    registry.register("baba", Object, color=(1, 0, 0))  # Red
    registry.register("wall", Object, color=(0.5, 0.5, 0.5))  # Gray
    registry.register("flag", Object, color=(1, 1, 0))  # Yellow
    registry.register("rock", Object, color=(0.6, 0.4, 0.2))  # Brown
    
    # Register text objects
    registry.register("text_baba", TextObject, text="BABA")
    registry.register("text_is", TextObject, text="IS")
    registry.register("text_you", TextObject, text="YOU")
    registry.register("text_wall", TextObject, text="WALL")
    registry.register("text_stop", TextObject, text="STOP")
    registry.register("text_flag", TextObject, text="FLAG")
    registry.register("text_win", TextObject, text="WIN")
    registry.register("text_rock", TextObject, text="ROCK")
    registry.register("text_push", TextObject, text="PUSH")
    
    # Place objects
    # Baba
    grid.place_object(registry.create("baba"), 2, 5)
    
    # Walls forming a barrier
    for x in range(4, 7):
        grid.place_object(registry.create("wall"), x, 3)
        grid.place_object(registry.create("wall"), x, 7)
    for y in range(4, 7):
        grid.place_object(registry.create("wall"), 4, y)
        grid.place_object(registry.create("wall"), 6, y)
    
    # Flag in the center
    grid.place_object(registry.create("flag"), 5, 5)
    
    # Rocks
    grid.place_object(registry.create("rock"), 3, 5)
    grid.place_object(registry.create("rock"), 7, 5)
    
    # Rules on the left side
    # BABA IS YOU
    grid.place_object(registry.create("text_baba"), 0, 0)
    grid.place_object(registry.create("text_is"), 1, 0)
    grid.place_object(registry.create("text_you"), 2, 0)
    
    # WALL IS STOP
    grid.place_object(registry.create("text_wall"), 0, 1)
    grid.place_object(registry.create("text_is"), 1, 1)
    grid.place_object(registry.create("text_stop"), 2, 1)
    
    # FLAG IS WIN
    grid.place_object(registry.create("text_flag"), 0, 2)
    grid.place_object(registry.create("text_is"), 1, 2)
    grid.place_object(registry.create("text_win"), 2, 2)
    
    # ROCK IS PUSH
    grid.place_object(registry.create("text_rock"), 0, 9)
    grid.place_object(registry.create("text_is"), 1, 9)
    grid.place_object(registry.create("text_push"), 2, 9)
    
    return grid

def main():
    """Create and play the custom level."""
    print("Custom Baba Is You Level")
    print("=" * 30)
    print("Objective: Reach the flag!")
    print("Hint: You might need to change the rules...")
    print()
    
    grid = create_custom_level()
    
    # Create a minimal environment wrapper for play
    class CustomEnv:
        def __init__(self, grid):
            self.grid = grid
            self._done = False
            self._reward = 0
        
        def reset(self):
            return self.grid.encode()
        
        def step(self, action):
            self.grid.step(action)
            self._done = self.grid.done
            self._reward = 1 if self.grid.won else 0
            return self.grid.encode(), self._reward, self._done, {}
        
        def render(self, mode='human'):
            self.grid.render()
    
    env = CustomEnv(grid)
    play(env)

if __name__ == "__main__":
    main()