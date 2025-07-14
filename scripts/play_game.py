#!/usr/bin/env python3
"""
Play Baba Is You with Claude Code SDK.
"""
import sys

from agent.claude_agent import ClaudeAgent
from baba.envs import list_environments

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
    
    print(f"🤖 Claude playing: {env_name}")
    print("Controls:")
    print("  SPACE: Pause/Resume")
    print("  ESC: Quit")
    print()
    
    # Create Claude agent
    agent = ClaudeAgent.create(
        env_name=env_name,
        delay=0.5,
        show_info_panel=True
    )
    
    try:
        # Play one episode
        won = agent.play_episode(max_steps=100)
        
        if won:
            print("\n🎉 Level completed!")
        else:
            print("\n⏱️ Time out - couldn't solve in 100 steps")
            
    finally:
        agent.cleanup()

if __name__ == "__main__":
    main()