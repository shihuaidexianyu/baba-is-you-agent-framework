"""
Baba Is You - Python implementation for AI agent development.
"""

# Core functionality
# Agent system
from .agent import Agent, UserAgent

from .grid import Grid
from .play import main as play_main
from .properties import Property


def make(*args, **kwargs):  # Deprecated stub
    """Deprecated: 内置环境已移除，请使用命令行参数 --world/--level 或 OfficialLevelEnvironment。"""
    raise RuntimeError(
        "Built-in environments have been removed. Use baba.play CLI with --world/--level or OfficialLevelEnvironment."
    )


def register(*args, **kwargs):  # Deprecated stub
    """Deprecated: 环境注册机制已移除。"""
    raise RuntimeError("Environment registry has been removed.")


__all__ = [
    # Core
    "make",
    "register",
    "Grid",
    "Property",
    # Agents
    "Agent",
    "UserAgent",
    # Play
    "play_main",
]
