#!/usr/bin/env python3
"""Demo the fun sprites in a custom Baba Is You level."""

from baba.envs import Environment
from baba.play import GamePlayer


class SpriteDemoEnvironment(Environment):
    """Demo environment showcasing all the fun sprites."""
    
    def __init__(self):
        super().__init__(15, 10, "SpriteDemo")
    
    def setup(self):
        """Set up a demo level with various sprites."""
        # Place walls around edges
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)
        
        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)
        
        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 5)
        
        # Place various objects
        # Rocks
        for x in [4, 5, 6]:
            rock = self.registry.create_instance("rock")
            self.grid.place_object(rock, x, 3)
        
        # Water pool
        for x in range(8, 11):
            for y in range(3, 6):
                water = self.registry.create_instance("water")
                self.grid.place_object(water, x, y)
        
        # Flags
        flag1 = self.registry.create_instance("flag")
        self.grid.place_object(flag1, 12, 2)
        
        flag2 = self.registry.create_instance("flag")
        self.grid.place_object(flag2, 12, 7)
        
        # More decorative elements
        rock2 = self.registry.create_instance("rock")
        self.grid.place_object(rock2, 7, 7)
        
        # Create rules section at the top
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)
        
        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)
        
        # ROCK IS PUSH
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        push_text = self.registry.create_instance("push", is_text=True)
        
        self.grid.place_object(rock_text, 5, 1)
        self.grid.place_object(is_text2, 6, 1)
        self.grid.place_object(push_text, 7, 1)
        
        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)
        
        self.grid.place_object(flag_text, 9, 1)
        self.grid.place_object(is_text3, 10, 1)
        self.grid.place_object(win_text, 11, 1)
        
        # WATER IS SINK
        water_text = self.registry.create_instance("water", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)
        sink_text = self.registry.create_instance("sink", is_text=True)
        
        self.grid.place_object(water_text, 1, 8)
        self.grid.place_object(is_text4, 2, 8)
        self.grid.place_object(sink_text, 3, 8)
        
        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text5 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)
        
        self.grid.place_object(wall_text, 5, 8)
        self.grid.place_object(is_text5, 6, 8)
        self.grid.place_object(stop_text, 7, 8)


def main():
    """Run the sprite demo."""
    print("Baba Is You - Sprite Demo")
    print("=" * 30)
    print("This level showcases our fun, unique sprites!")
    print("Notice:")
    print("  - Baba has cute ears (▲▲)")
    print("  - Walls have a brick pattern")
    print("  - Rocks are rough circles")
    print("  - Water has wavy patterns (~)")
    print("  - Flags are waving")
    print("  - Text objects have distinct colors")
    print()
    print("Controls:")
    print("  Arrow keys: Move")
    print("  R: Reset")
    print("  ESC: Quit")
    print()
    
    # Create and play the demo
    env = SpriteDemoEnvironment()
    player = GamePlayer("simple", cell_size=48)
    player.env = env
    player.setup_display()
    player.run()


if __name__ == "__main__":
    main()