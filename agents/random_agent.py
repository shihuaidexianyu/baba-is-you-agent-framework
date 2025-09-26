"""
Baba Is You 的随机 Agent。

该简单 Agent 展示了最小化的 Agent 接口用法。
它只会随机选择动作。
"""

import random

from baba.agent import Agent
from baba.grid import Grid


class RandomAgent(Agent):
    """采取随机动作的 Agent。"""

    def __init__(self):
        super().__init__("Random Agent")
        self.actions = ["up", "down", "left", "right", "wait"]

    def get_action(self, observation: Grid) -> str:  # noqa: ARG002
        """随机选择一个动作。"""
        return random.choice(self.actions)


# 示例用法
if __name__ == "__main__":
    from baba import create_environment

    # Create agent and environment
    agent = RandomAgent()
    env = create_environment("simple")

    # Play one episode with visualization
    stats = agent.play_episode(env, render=True, verbose=True)

    # Or play many episodes without visualization
    # stats = agent.play_episodes(env, num_episodes=100, render=False)
    # print(f"Win rate: {stats['win_rate']*100:.1f}%")
