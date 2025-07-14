"""
Baba Is You agent framework.
"""

from .baba_agent import (
    BabaAgent,
    DecisionMaker,
    GameObservation,
    AgentDecision,
    Action,
    SimplePathfindingDecisionMaker
)

# Optional Claude integration
try:
    from .claude_agent import ClaudeAgent, ClaudeDecisionMaker
    __all__ = [
        'BabaAgent',
        'DecisionMaker', 
        'GameObservation',
        'AgentDecision',
        'Action',
        'SimplePathfindingDecisionMaker',
        'ClaudeAgent',
        'ClaudeDecisionMaker'
    ]
except ImportError:
    # Claude not available
    __all__ = [
        'BabaAgent',
        'DecisionMaker',
        'GameObservation', 
        'AgentDecision',
        'Action',
        'SimplePathfindingDecisionMaker'
    ]