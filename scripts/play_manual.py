#!/usr/bin/env python3
"""
Play Baba Is You manually (human player).

This is a convenience script that launches the game with UserAgent.
It's equivalent to: pixi run play --agent user
"""

import sys
from baba.play import play
from baba.envs import list_environments

def main():
    # Get environment from command line or use default
    env_name = "simple"
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if env_name not in list_environments():
            print(f"Environment '{env_name}' not found.")
            print(f"Available environments: {', '.join(list_environments())}")
            return 1
    
    print(f"🎮 Manual play: {env_name}")
    print("Controls:")
    print("  Arrow keys or WASD: Move")
    print("  Space: Wait")  
    print("  R: Reset level")
    print("  Q/ESC: Quit")
    print()
    
    # Play with human control
    stats = play(
        env_name=env_name,
        agent_type="user",
        episodes=1,
        render=True,
        verbose=True
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())