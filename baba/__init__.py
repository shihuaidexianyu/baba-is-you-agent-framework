from .envs import create_environment, list_environments
from .play import GamePlayer

# Create aliases for compatibility
def make(env_name):
    """Create an environment by name."""
    # Handle both formats: "simple" and "SimpleEnvironment-v0"
    if env_name.endswith("-v0"):
        # Extract the base name
        base_name = env_name[:-3]  # Remove "-v0"
        # Convert from CamelCase to snake_case
        import re
        base_name = re.sub('Environment$', '', base_name)
        base_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', base_name).lower()
        env_name = base_name
    
    return create_environment(env_name)

def register(name, env_class):
    """Register a new environment."""
    from .envs import ENVIRONMENTS
    ENVIRONMENTS[name] = env_class

def play(env):
    """Play an environment interactively."""
    player = GamePlayer(env.name if hasattr(env, 'name') else 'custom')
    player.env = env
    player.run()