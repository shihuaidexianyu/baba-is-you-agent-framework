#!/usr/bin/env python3
"""
Claude Code SDK-powered decision maker for Baba Is You.

This module implements a DecisionMaker that uses Claude Code SDK to analyze
game states and make intelligent decisions.
"""

import json
import asyncio
from typing import Dict, Any, Optional

from .baba_agent import DecisionMaker, GameObservation, AgentDecision, Action

# Optional import for Claude Code SDK
try:
    from claude_code_sdk import query, ClaudeCodeOptions
    import anyio
    HAS_CLAUDE_CODE = True
except ImportError:
    HAS_CLAUDE_CODE = False


class ClaudeDecisionMaker(DecisionMaker):
    """
    Decision maker that uses Claude Code SDK to analyze game states and choose actions.
    
    This implementation sends structured game observations to Claude and
    interprets the responses as game actions.
    """
    
    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initialize the Claude decision maker.
        
        Args:
            system_prompt: Optional system prompt to customize Claude's behavior
        """
        if not HAS_CLAUDE_CODE:
            raise ImportError("claude-code-sdk required. Install with: pip install claude-code-sdk")
        
        self.system_prompt = system_prompt or """You are an expert Baba Is You player. 
You analyze game states and decide the best moves to win puzzles.
You MUST respond with ONLY a valid JSON object in this exact format:
{{"action": "UP", "reasoning": "Moving toward the flag", "confidence": 0.8}}
Do not include any other text, markdown formatting, or explanation."""
        
        self.conversation_history = []
        
    def reset(self):
        """Reset conversation history for new episode."""
        self.conversation_history = []
    
    def decide(self, observation: GameObservation) -> AgentDecision:
        """
        Use Claude to analyze the game state and decide on an action.
        
        Args:
            observation: Current game state
            
        Returns:
            AgentDecision with Claude's chosen action and reasoning
        """
        # Build the prompt
        prompt = self._build_prompt(observation)
        
        try:
            # Run async query in sync context
            return asyncio.run(self._async_decide(prompt))
            
        except Exception as e:
            # Fallback to simple exploration on error
            print(f"Claude Code SDK error: {e}")
            return AgentDecision(
                action=Action.RIGHT,
                reasoning=f"SDK error, exploring right",
                confidence=0.1
            )
    
    async def _async_decide(self, prompt: str) -> AgentDecision:
        """Async method to query Claude and get decision."""
        options = ClaudeCodeOptions(
            system_prompt=self.system_prompt,
            max_turns=1  # Single turn for decision making
        )
        
        response_text = ""
        async for message in query(prompt=prompt, options=options):
            # Handle different message types from Claude Code SDK
            if hasattr(message, 'content'):
                content = message.content
                if isinstance(content, list):
                    # Extract text from list of content blocks
                    for block in content:
                        if hasattr(block, 'text'):
                            response_text += block.text
                        elif isinstance(block, str):
                            response_text += block
                elif isinstance(content, str):
                    response_text += content
            elif isinstance(message, str):
                response_text += message
            else:
                # Skip non-text messages (like SystemMessage)
                continue
        
        return self._parse_response(response_text)
    
    def _build_prompt(self, observation: GameObservation) -> str:
        """Build a prompt for Claude based on the game observation."""
        # Get controlled objects
        controlled = observation.controlled_objects
        if not controlled:
            controlled_desc = "No objects under your control"
        else:
            controlled_desc = ", ".join(f"{obj['type']} at ({obj['x']}, {obj['y']})" 
                                      for obj in controlled)
        
        # Get win objects
        win_objs = observation.win_objects
        if not win_objs:
            win_desc = "No winning objects visible"
        else:
            win_desc = ", ".join(f"{obj['type']} at ({obj['x']}, {obj['y']})" 
                               for obj in win_objs)
        
        # Get pushable text objects
        text_objs = [obj for obj in observation.pushable_objects if obj.get('is_text', False)]
        if not text_objs:
            text_desc = "No text objects visible"
        else:
            text_desc = ", ".join(f"{obj['type']} at ({obj['x']}, {obj['y']})" 
                                for obj in text_objs)
        
        # Get stop objects
        stop_objs = observation.stop_objects
        if not stop_objs:
            stop_desc = "No blocking objects"
        else:
            stop_desc = ", ".join(f"{obj['type']} at ({obj['x']}, {obj['y']})" 
                                for obj in stop_objs[:5])  # Limit to first 5
            if len(stop_objs) > 5:
                stop_desc += f" and {len(stop_objs) - 5} more"
        
        prompt = f"""You are playing Baba Is You, a puzzle game where you can change the rules by pushing text blocks.

Current game state:
- You control: {controlled_desc}
- Win objects: {win_desc}
- Text objects: {text_desc}
- Blocking objects: {stop_desc}
- Active rules: {', '.join(observation.active_rules) if observation.active_rules else 'None'}

Your goal is to reach a WIN object or create a rule that makes you WIN.

You MUST respond with ONLY a JSON object (no markdown, no extra text) in this exact format:
{{"action": "RIGHT", "reasoning": "Moving toward FLAG which is WIN", "confidence": 0.9}}

Valid actions are: UP, DOWN, LEFT, RIGHT
The reasoning should be under 50 words.
Confidence should be between 0 and 1.

Respond with your JSON decision:"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> AgentDecision:
        """Parse Claude's response into an AgentDecision."""
        try:
            # Clean up response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
                response_text = response_text.strip()
            
            # Try to parse as JSON directly first
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            
            # Parse action
            action_str = data.get('action', 'RIGHT').upper()
            action = Action.from_string(action_str)
            if not action:
                action = Action.RIGHT  # Default fallback
            
            # Get reasoning and confidence
            reasoning = data.get('reasoning', 'No reasoning provided')
            confidence = float(data.get('confidence', 0.5))
            
            return AgentDecision(
                action=action,
                reasoning=reasoning,
                confidence=min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
            )
                
        except Exception as e:
            print(f"Failed to parse Claude response: {response_text[:200]}")
            # Complete fallback - just go right
            return AgentDecision(
                action=Action.RIGHT,
                reasoning=f"Parse error: {str(e)[:30]}",
                confidence=0.1
            )


class ClaudeAgent:
    """
    Convenience class that creates a BabaAgent with ClaudeDecisionMaker.
    
    This is a simple wrapper to make it easy to create a Claude-powered agent.
    """
    
    @staticmethod
    def create(env_name: str = "simple", 
               system_prompt: Optional[str] = None,
               **kwargs) -> 'BabaAgent':
        """
        Create a BabaAgent that uses Claude Code SDK for decision making.
        
        Args:
            env_name: Environment to play
            system_prompt: Optional system prompt to customize Claude's behavior
            **kwargs: Additional arguments passed to BabaAgent
            
        Returns:
            BabaAgent configured with ClaudeDecisionMaker
        """
        from .baba_agent import BabaAgent
        
        decision_maker = ClaudeDecisionMaker(system_prompt=system_prompt)
        
        return BabaAgent(
            env_name=env_name,
            decision_maker=decision_maker,
            **kwargs
        )


# Example usage
if __name__ == "__main__":
    # Example of using ClaudeAgent
    agent = ClaudeAgent.create(
        env_name="simple",
        delay=0.5,
        show_info_panel=True
    )
    
    try:
        won = agent.play_episode(max_steps=100)
        print(f"\nResult: {'Won!' if won else 'Lost/Timeout'}")
    finally:
        agent.cleanup()