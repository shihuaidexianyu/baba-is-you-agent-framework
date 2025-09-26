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

    # 建议直接使用命令行（平铺式）：
    #   python -m baba.play --level-name 1level --map-dir map
    # 或
    #   python -m baba.play --level-file map/1level.l
    # 如需脚本内运行，设置环境变量 LEVEL_NAME 或 LEVEL_FILE，再执行本脚本。
    map_dir = os.environ.get("MAP_DIR", "map")
    level_name = os.environ.get("LEVEL_NAME")  # 如 1level / n1level
    level_file = os.environ.get("LEVEL_FILE")  # 如 map/1level.l
    if not (level_name or level_file):
        raise SystemExit("Please set LEVEL_NAME (e.g., 1level) or LEVEL_FILE (path to .l). Or use CLI: python -m baba.play --level-name 1level --map-dir map")

    env = OfficialLevelEnvironment(level_name=level_name, level_file=level_file, map_dir=map_dir)
    agent = RandomAgent()
    stats = agent.play_episode(env, render=True, verbose=True)
