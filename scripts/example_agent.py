#!/usr/bin/env python3
"""
Example script showing how to create an agent for Baba Is You.
"""
import sys

import numpy as np
from baba import make

class RandomAgent:
    """Simple random agent that takes random actions."""
    
    def __init__(self):
        self.action_space = [0, 1, 2, 3]  # up, right, down, left
    
    def act(self, observation):
        """Choose a random action."""
        return np.random.choice(self.action_space)

def run_agent(env_name="SimpleEnvironment-v0", num_episodes=5, max_steps=100):
    """Run the random agent for a specified number of episodes."""
    env = make(env_name)
    agent = RandomAgent()
    
    for episode in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        
        print(f"\nEpisode {episode + 1}")
        print("-" * 20)
        
        for step in range(max_steps):
            # Agent chooses action
            action = agent.act(obs)
            
            # Take action in environment
            obs, reward, done, info = env.step(action)
            total_reward += reward
            
            if done:
                if reward > 0:
                    print(f"Episode completed successfully! Steps: {step + 1}, Reward: {total_reward}")
                else:
                    print(f"Episode failed. Steps: {step + 1}, Reward: {total_reward}")
                break
        else:
            print(f"Episode timed out. Steps: {max_steps}, Reward: {total_reward}")
        
        # Render final state
        env.render()

if __name__ == "__main__":
    env_name = "SimpleEnvironment-v0"
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
    
    print(f"Running Random Agent on {env_name}")
    run_agent(env_name)