#!/usr/bin/env python3
"""List all available Baba Is You environments."""

from baba.envs import list_environments, create_environment


def main():
    """List and describe all available environments."""
    print("Available Baba Is You Environments")
    print("=" * 50)
    print()
    
    environments = sorted(list_environments())
    
    # Group environments by category
    basic = []
    extended = []
    advanced = []
    
    for env_name in environments:
        if env_name in ["simple", "wall_maze", "push_puzzle", "transformation"]:
            basic.append(env_name)
        elif env_name in ["make_you", "transform_puzzle", "multi_rule", "rule_chain"]:
            advanced.append(env_name)
        else:
            extended.append(env_name)
    
    # Print basic environments
    print("BASIC ENVIRONMENTS (Original)")
    print("-" * 30)
    for env_name in basic:
        env = create_environment(env_name)
        print(f"  {env_name:<20} - {env.name}")
    
    print()
    print("EXTENDED ENVIRONMENTS (From baba-is-ai)")
    print("-" * 30)
    for env_name in extended:
        env = create_environment(env_name)
        print(f"  {env_name:<20} - {env.name}")
    
    print()
    print("ADVANCED ENVIRONMENTS (Complex puzzles)")
    print("-" * 30)
    for env_name in advanced:
        env = create_environment(env_name)
        print(f"  {env_name:<20} - {env.name}")
    
    print()
    print("To play an environment, run:")
    print("  python scripts/play_game.py <environment_name>")
    print()
    print("Examples:")
    print("  python scripts/play_game.py simple")
    print("  python scripts/play_game.py two_room_break_stop")
    print("  python scripts/play_game.py make_you")
    
    # Descriptions
    print()
    print()
    print("ENVIRONMENT DESCRIPTIONS")
    print("=" * 50)
    
    descriptions = {
        # Basic
        "simple": "Basic level - reach the flag to win",
        "wall_maze": "Navigate through a maze of walls",
        "push_puzzle": "Push objects to solve the puzzle",
        "transformation": "Transform objects using rules",
        
        # Extended
        "you_win": "Simple level where you just need to reach the win object",
        "make_win": "Create a WIN rule by pushing text blocks together",
        "two_room": "Two rooms separated by a wall with a gap",
        "two_room_break_stop": "Break WALL IS STOP to pass between rooms",
        "make_win_distr": "Make WIN with distractor objects and rules",
        "goto_win_color": "Multiple colored objects, specific one wins",
        
        # Advanced
        "make_you": "Transfer control to another object with YOU rule",
        "transform_puzzle": "Use transformation to cross barriers",
        "multi_rule": "Complex level with multiple interacting rules",
        "rule_chain": "Sequential rule changes required to win"
    }
    
    for category, envs in [("Basic", basic), ("Extended", extended), ("Advanced", advanced)]:
        if envs:
            print(f"\n{category}:")
            print("-" * 30)
            for env_name in envs:
                desc = descriptions.get(env_name, "No description available")
                print(f"{env_name}:")
                print(f"  {desc}")


if __name__ == "__main__":
    main()