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
    import os
    from baba.envs import OfficialLevelEnvironment

    # 建议直接使用命令行：
    #   python -m baba.play --world <world> --level <n> --map-dir map
    # 如需脚本内运行，设置环境变量 WORLD/LEVEL/MAP_DIR，然后执行本脚本。
    world = os.environ.get("WORLD")
    level = os.environ.get("LEVEL")
    map_dir = os.environ.get("MAP_DIR", "map")
    if not (world and level):
        raise SystemExit("Please set WORLD and LEVEL env vars, or run via CLI: python -m baba.play --world <world> --level <n> --map-dir map")

    env = OfficialLevelEnvironment(world=world, level=int(level), map_dir=map_dir)
    agent = RandomAgent()
    stats = agent.play_episode(env, render=True, verbose=True)
