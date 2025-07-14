"""
Main entry point for playing Baba Is You.

Provides a simple interface to play the game with different agents.
"""

import argparse
import sys
from typing import Optional

from .agent import UserAgent, ClaudeCodeAgent
from .envs import create_environment, list_environments
from .episode_player import EpisodePlayer


def play(
    env_name: str = "simple",
    agent_type: str = "user",
    episodes: int = 1,
    render: bool = True,
    cell_size: int = 48,
    fps: int = 30,
    verbose: bool = True
) -> dict:
    """
    Play Baba Is You with the specified configuration.
    
    Args:
        env_name: Name of the environment to play
        agent_type: Type of agent ("user" or "claude")
        episodes: Number of episodes to play
        render: Whether to render visually
        cell_size: Size of each cell in pixels
        fps: Frames per second for rendering
        verbose: Whether to print information
        
    Returns:
        Dictionary with episode statistics
    """
    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Environment '{env_name}' not found.")
        print(f"Available environments: {', '.join(list_environments())}")
        sys.exit(1)
        
    # Create agent
    if agent_type == "user":
        agent = UserAgent()
    elif agent_type == "claude":
        agent = ClaudeCodeAgent()
    else:
        print(f"Unknown agent type: {agent_type}")
        print("Available agents: user, claude")
        sys.exit(1)
        
    # Create episode player
    player = EpisodePlayer(
        env=env,
        agent=agent,
        render=render,
        cell_size=cell_size,
        fps=fps,
        verbose=verbose
    )
    
    # Play episodes
    return player.play_episodes(episodes)


def main():
    """Command-line interface for playing Baba Is You."""
    parser = argparse.ArgumentParser(
        description="Play Baba Is You",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Play interactively (default)
  pixi run play
  
  # Play specific environment
  pixi run play --env push_puzzle
  
  # Watch Claude play
  pixi run play --agent claude
  
  # Run Claude on multiple episodes without rendering
  pixi run play --agent claude --episodes 10 --no-render
"""
    )
    
    parser.add_argument(
        "--env",
        default="simple",
        choices=list_environments(),
        help="Environment to play (default: simple)"
    )
    
    parser.add_argument(
        "--agent",
        default="user",
        choices=["user", "claude"],
        help="Agent type (default: user)"
    )
    
    parser.add_argument(
        "--episodes",
        type=int,
        default=1,
        help="Number of episodes to play (default: 1)"
    )
    
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Disable visual rendering"
    )
    
    parser.add_argument(
        "--cell-size",
        type=int,
        default=48,
        help="Size of each cell in pixels (default: 48)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose output"
    )
    
    args = parser.parse_args()
    
    # Play the game
    stats = play(
        env_name=args.env,
        agent_type=args.agent,
        episodes=args.episodes,
        render=not args.no_render,
        cell_size=args.cell_size,
        fps=args.fps,
        verbose=not args.quiet
    )
    
    return 0 if stats.get('wins', 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())