"""
Baba Is You - Python implementation for AI agent development.
"""

# Core functionality
from .envs import create_environment, list_environments
from .grid import Grid
from .properties import Property

# Agent system
from .agent import Agent, UserAgent, ClaudeCodeAgent
from .episode_player import EpisodePlayer

# Play functionality
from .play import play, main as play_main


def make(env_name):
    """
    Create an environment by name.
    
    Args:
        env_name: Name of the environment
        
    Returns:
        Environment instance
    """
    return create_environment(env_name)


def register(name, env_class):
    """
    Register a new environment.
    
    Args:
        name: Name for the environment
        env_class: Environment class
    """
    from .envs import ENVIRONMENTS
    ENVIRONMENTS[name] = env_class


__all__ = [
    # Core
    'make',
    'register',
    'create_environment',
    'list_environments',
    'Grid',
    'Property',
    
    # Agents
    'Agent',
    'UserAgent', 
    'ClaudeCodeAgent',
    'EpisodePlayer',
    
    # Play
    'play',
    'play_main',
]