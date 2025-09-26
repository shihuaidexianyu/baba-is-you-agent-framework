"""
Baba Is You 的预配置关卡环境。

该模块提供了一组即玩型关卡，从简单教程到复杂谜题不等。每个环境展示
不同的游戏机制与规则交互。

这些环境旨在用于教学与挑战，涵盖：
- 基本移动与胜利条件
- 推动机制与障碍物绕行
- 物体变形（Transformation）
- 复杂规则的拼接与修改
- 高级属性，如 SINK、HOT/MELT 等
"""

import numpy as np
from pathlib import Path

from .grid import Grid
from .registration import Registry
from .level_loader import LevelLoader


class Environment:
    """
    Baba Is You 关卡环境的基类。

    每个环境代表一个谜题关卡，包含：
    - 固定尺寸
    - 初始物体布局
    - 起始规则（由文字方块拼成）

    子类需实现 setup() 来构建具体谜题。
    """

    def __init__(self, width: int, height: int, name: str = "Custom"):
        """
        初始化环境。

        创建网格与注册表，然后调用 setup() 将物体与规则放入关卡。

        参数：
            width: 网格宽度（单位：格）
            height: 网格高度（单位：格）
            name: 环境显示名称
        """
        self.width = width
        self.height = height
        self.name = name
        self.registry = Registry()
        self.grid = Grid(width, height, self.registry)

        # Set up the initial state
        self.setup()

        # Update rules after setup
        # This is crucial - rules must be extracted after all text is placed
        self.grid._update_rules()

    def setup(self):
        """
        设置环境的初始状态。

        子类应完成：
        1. 放置游戏物体（baba、rock、wall 等）
        2. 放置文字方块以拼接规则
        3. 布局谜题结构

        在 __init__ 与 reset() 中会自动调用。
        """
        pass

    def reset(self) -> Grid:
        """
        将环境重置为初始状态。

        会重建网格并再次调用 setup()。常用于胜/负后重开关卡。

        返回：
            新创建的网格（观测）
        """
        self.grid = Grid(self.width, self.height, self.registry)
    """从本地官方关卡目录加载特定关卡的环境。

    - 关卡文件应放在工作区的 `map/` 目录下，结构类似：
      map/<world>/<n>level.l 和 map/<world>/<n>level.ld
    - 使用 `LevelLoader(worlds_path=Path('map'))` 读取。
    """

    def __init__(self, world: str, level: int, map_dir: str = "map"):
        self.world = world
        self.level = level
        self.map_dir = map_dir

        # 先创建一个占位网格，稍后在 setup() 中用真实关卡替换
        super().__init__(width=12, height=12, name=f"{world}:{level}")

    def setup(self):
        loader = LevelLoader(worlds_path=Path(self.map_dir))
        grid = loader.load_level(self.world, self.level, self.registry)
        if grid is None:
            # 加载失败则创建一个简单提示关卡
            self.grid = Grid(self.width, self.height, self.registry)
            # 放一个文本：BABA IS YOU，FLAG IS WIN，和一个 FLAG
            baba = self.registry.create_instance("baba")
            self.grid.place_object(baba, 1, 1)
            baba_t = self.registry.create_instance("baba", is_text=True)
            is_t = self.registry.create_instance("is", is_text=True)
            you_t = self.registry.create_instance("you", is_text=True)
            self.grid.place_object(baba_t, 1, 3)
            self.grid.place_object(is_t, 2, 3)
            self.grid.place_object(you_t, 3, 3)
            flag = self.registry.create_instance("flag")
            self.grid.place_object(flag, 8, 8)
            flag_t = self.registry.create_instance("flag", is_text=True)
            win_t = self.registry.create_instance("win", is_text=True)
            is_t2 = self.registry.create_instance("is", is_text=True)
            self.grid.place_object(flag_t, 7, 1)
            self.grid.place_object(is_t2, 8, 1)
            self.grid.place_object(win_t, 9, 1)
            self.name = f"{self.world}:{self.level} (fallback)"
        else:
            # 使用加载的网格与尺寸
            self.grid = grid
            self.width = grid.width
            self.height = grid.height
            self.name = f"{self.world}:{self.level}"
        # 更新规则
        self.grid._update_rules()
        self.setup()

        # Update rules after setup
        self.grid._update_rules()

        return self.grid

    def step(self, action: str) -> tuple[Grid, float, bool, dict]:
        """
        在环境中执行一步（接口风格类似 Gym）。

        参数：
            action: 取值为 ["up", "down", "left", "right", "wait"] 之一

        返回：
            observation: 新状态的 Grid 对象
            reward: 胜利为 1.0、失败为 -1.0、其他为 0.0
            done: 若回合结束（胜/负）则为 True
            info: 额外信息字典
        """
        # Take the action
        won, lost = self.grid.step(action)

        # Compute reward
        reward = 0.0
        if won:
            reward = 1.0
        elif lost:
            reward = -1.0

        # 胜/负即视为回合结束
        done = won or lost

        # 额外信息
        info = {
            "won": won,
            "lost": lost,
            "steps": self.grid.steps,
            "rules": [str(rule) for rule in self.grid.rule_manager.rules],
        }

        return self.grid, reward, done, info

    def render(self, mode: str = "rgb_array", cell_size: int = 24) -> np.ndarray:  # noqa: ARG002
        """
        渲染当前状态。

        参数：
            mode: 渲染模式（"rgb_array" 返回 numpy 数组）
            cell_size: 每格像素大小

        返回：
            RGB 图像（numpy 数组）
        """
        return self.grid.render(cell_size)

    def get_state(self):
        """获取当前状态。"""
        return self.grid.get_state()


# Basic Environments


class SimpleEnvironment(Environment):
    """
    具备基础规则的简单测试环境。

    最基础的关卡——教授移动与胜利条件。
    布局：左侧为 Baba，右侧为旗帜，上方给出规则。
    目标：将 Baba 移动到旗帜位置。
    """

    def __init__(self):
        super().__init__(10, 10, "Simple")

    def setup(self):
        """
        设置一个简单关卡。

        创建：
        - BABA IS YOU（玩家可控制）
        - FLAG IS WIN（胜利目标）
        """
        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 5)

        # Place flag
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 8, 5)

        # Create rules: BABA IS YOU
        # Text objects form rules when aligned horizontally/vertically
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # Create rules: FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 6, 1)
        self.grid.place_object(is_text2, 7, 1)
        self.grid.place_object(win_text, 8, 1)


class WallMazeEnvironment(Environment):
    """由墙体构成迷宫的环境。"""

    def __init__(self):
        super().__init__(12, 12, "Wall Maze")

    def setup(self):
        """设置迷宫关卡。"""
        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 1, 1)

        # Place flag
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 10, 10)

        # Create walls for maze
        wall_positions = [
            # Outer walls
            *[(x, 0) for x in range(12)],
            *[(x, 11) for x in range(12)],
            *[(0, y) for y in range(1, 11)],
            *[(11, y) for y in range(1, 11)],
            # Inner maze walls
            *[(x, 3) for x in range(1, 9)],
            *[(9, y) for y in range(1, 9)],
            *[(x, 7) for x in range(3, 11)],
            (3, 5),
            (3, 6),
            (3, 8),
            (3, 9),
            (5, 5),
            (6, 5),
            (7, 5),
        ]

        for x, y in wall_positions:
            wall = self.registry.create_instance("wall")
            self.grid.place_object(wall, x, y)

    # 在安全区域创建规则
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 10)
        self.grid.place_object(is_text, 2, 10)
        self.grid.place_object(you_text, 3, 10)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 5, 10)
        self.grid.place_object(is_text2, 6, 10)
        self.grid.place_object(win_text, 7, 10)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 1, 2)
        self.grid.place_object(is_text3, 2, 2)
        self.grid.place_object(stop_text, 3, 2)


class PushPuzzleEnvironment(Environment):
    """聚焦于推动机制的环境。"""

    def __init__(self):
        super().__init__(10, 8, "Push Puzzle")

    def setup(self):
        """设置推动类谜题。"""
        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 1, 4)

        # Place rocks to push
        rock_positions = [(3, 4), (5, 4), (7, 4)]
        for x, y in rock_positions:
            rock = self.registry.create_instance("rock")
            self.grid.place_object(rock, x, y)

        # Place flag
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 9, 4)

        # Create walls
        wall_positions = [
            *[(x, 2) for x in range(2, 9)],
            *[(x, 6) for x in range(2, 9)],
            (2, 3),
            (2, 5),
            (8, 3),
            (8, 5),
        ]

        for x, y in wall_positions:
            wall = self.registry.create_instance("wall")
            self.grid.place_object(wall, x, y)

    # 创建规则
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 0)
        self.grid.place_object(is_text, 2, 0)
        self.grid.place_object(you_text, 3, 0)

        # ROCK IS PUSH
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        push_text = self.registry.create_instance("push", is_text=True)

        self.grid.place_object(rock_text, 5, 0)
        self.grid.place_object(is_text2, 6, 0)
        self.grid.place_object(push_text, 7, 0)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 1, 7)
        self.grid.place_object(is_text3, 2, 7)
        self.grid.place_object(win_text, 3, 7)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 5, 7)
        self.grid.place_object(is_text4, 6, 7)
        self.grid.place_object(stop_text, 7, 7)


class TransformationEnvironment(Environment):
    """展示物体变形机制的环境。"""

    def __init__(self):
        super().__init__(10, 10, "Transformation")

    def setup(self):
        """设置变形谜题。"""
        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 5)

    # 放置水（障碍）
        water_positions = [(x, 5) for x in range(4, 7)]
        for x, y in water_positions:
            water = self.registry.create_instance("water")
            self.grid.place_object(water, x, y)

        # Place flag
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 8, 5)

    # 放置石头（用于变形）
        rock_positions = [(2, 3), (2, 7)]
        for x, y in rock_positions:
            rock = self.registry.create_instance("rock")
            self.grid.place_object(rock, x, y)

    # 创建初始规则
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 6, 1)
        self.grid.place_object(is_text2, 7, 1)
        self.grid.place_object(win_text, 8, 1)

    # WATER IS SINK
        water_text = self.registry.create_instance("water", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        sink_text = self.registry.create_instance("sink", is_text=True)

        self.grid.place_object(water_text, 1, 9)
        self.grid.place_object(is_text3, 2, 9)
        self.grid.place_object(sink_text, 3, 9)

    # ROCK IS（未完成——待拼接）
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)

        self.grid.place_object(rock_text, 6, 9)
        self.grid.place_object(is_text4, 7, 9)

    # BABA 文字（用于变形规则）
        baba_text2 = self.registry.create_instance("baba", is_text=True)
        self.grid.place_object(baba_text2, 8, 9)


# Extended Environments (from baba-is-ai)


class YouWinEnvironment(Environment):
    """简单环境——只需抵达胜利物体。"""

    def __init__(self):
        super().__init__(6, 6, "YouWin")

    def setup(self):
        """设置一个简单的胜利关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

        # Place inner walls
        for x, y in [(1, 3), (1, 4), (4, 3), (4, 4)]:
            wall = self.registry.create_instance("wall")
            self.grid.place_object(wall, x, y)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 2)

        # Place win object (flag)
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 3, 3)

    # 创建规则
    # BABA IS YOU（不可破坏）
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 1, 2)
        self.grid.place_object(is_text2, 2, 2)
        self.grid.place_object(win_text, 3, 2)


class MakeWinEnvironment(Environment):
    """需要先创建胜利规则才能获胜的环境。"""

    def __init__(self):
        super().__init__(8, 8, "MakeWin")

    def setup(self):
        """设置“先造胜利再取胜”的关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 2)

        # Place rock (target for win rule)
        rock = self.registry.create_instance("rock")
        self.grid.place_object(rock, 5, 5)

    # 创建规则
    # BABA IS YOU（固定位置）
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

    # 残缺的 ROCK IS WIN 规则
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

    # 将文字分开放置，迫使玩家推动拼接
        self.grid.place_object(rock_text, 2, 4)
        self.grid.place_object(is_text2, 4, 3)
        self.grid.place_object(win_text, 6, 4)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 5, 1)
        self.grid.place_object(is_text3, 6, 1)
        self.grid.place_object(stop_text, 7, 1)


class TwoRoomEnvironment(Environment):
    """两间房间，中间有分隔墙的环境。"""

    def __init__(self):
        super().__init__(13, 9, "TwoRoom")

    def setup(self):
        """设置双房间关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

    # 放置分隔墙
        for y in range(1, self.height - 1):
            if y != 4:  # Leave a gap
                wall = self.registry.create_instance("wall")
                self.grid.place_object(wall, 6, y)

    # 左侧房间放置 Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 4)

    # 右侧房间放置旗帜
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 10, 4)

    # 在左侧房间创建规则
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 7, 1)
        self.grid.place_object(is_text2, 8, 1)
        self.grid.place_object(win_text, 9, 1)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 1, 7)
        self.grid.place_object(is_text3, 2, 7)
        self.grid.place_object(stop_text, 3, 7)


class TwoRoomBreakStopEnvironment(Environment):
    """两间房间的环境，需要破坏 WALL IS STOP 才能通过。"""

    def __init__(self):
        super().__init__(13, 9, "TwoRoomBreakStop")

    def setup(self):
        """设置需要破坏 WALL IS STOP 的双房间关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

    # 放置完整的分隔墙（无缺口）
        for y in range(1, self.height - 1):
            wall = self.registry.create_instance("wall")
            self.grid.place_object(wall, 6, y)

    # 左侧房间放置 Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 4)

    # 右侧房间放置旗帜
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 10, 4)

    # 创建规则
    # BABA IS YOU（固定）
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

    # FLAG IS WIN（位于右侧房间）
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 7, 1)
        self.grid.place_object(is_text2, 8, 1)
        self.grid.place_object(win_text, 9, 1)

    # WALL IS STOP（可被破坏——位于左侧房间）
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 2, 6)
        self.grid.place_object(is_text3, 3, 6)
        self.grid.place_object(stop_text, 4, 6)


class MakeWinWithDistractorsEnvironment(Environment):
    """带有干扰物体与规则的“造胜利”环境。"""

    def __init__(self):
        super().__init__(10, 10, "MakeWinDistr")

    def setup(self):
        """设置含干扰项的“先造胜利再取胜”关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 2)

    # 放置目标物体（rock）
        rock = self.registry.create_instance("rock")
        self.grid.place_object(rock, 7, 7)

    # 放置干扰物体
        water = self.registry.create_instance("water")
        self.grid.place_object(water, 4, 4)

        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 5, 6)

    # 创建规则
    # BABA IS YOU（固定）
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

    # 残缺的 ROCK IS WIN 规则
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(rock_text, 2, 5)
        self.grid.place_object(is_text2, 5, 3)
        self.grid.place_object(win_text, 8, 5)

    # 干扰用的规则碎片
        water_text = self.registry.create_instance("water", is_text=True)
        sink_text = self.registry.create_instance("sink", is_text=True)
        push_text = self.registry.create_instance("push", is_text=True)

        self.grid.place_object(water_text, 7, 2)
        self.grid.place_object(sink_text, 8, 3)
        self.grid.place_object(push_text, 6, 8)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 6, 1)
        self.grid.place_object(is_text3, 7, 1)
        self.grid.place_object(stop_text, 8, 1)


class GotoWinWithColorEnvironment(Environment):
    """带“颜色”概念的环境（特定颜色可胜利）。"""

    def __init__(self):
        super().__init__(8, 8, "GotoWinColor")

    def setup(self):
        """设置包含“颜色”物体的关卡。"""
        # Place walls around perimeter
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 4)

        # 放置多块带不同“颜色”的石头（用位置代表）
        rock1 = self.registry.create_instance("rock")
        rock1.color = (255, 0, 0)  # 红
        self.grid.place_object(rock1, 4, 2)

        rock2 = self.registry.create_instance("rock")
        rock2.color = (0, 255, 0)  # 绿
        self.grid.place_object(rock2, 5, 4)

        rock3 = self.registry.create_instance("rock")
        rock3.color = (0, 0, 255)  # 蓝
        self.grid.place_object(rock3, 4, 6)

        # Create rules
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # ROCK IS WIN（为简化：所有 rock 都算胜利）
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(rock_text, 1, 2)
        self.grid.place_object(is_text2, 2, 2)
        self.grid.place_object(win_text, 3, 2)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 5, 1)
        self.grid.place_object(is_text3, 6, 1)
        self.grid.place_object(stop_text, 7, 1)


# Advanced Environments


class MakeYouEnvironment(Environment):
    """需要创造新的 YOU 规则的环境。"""

    def __init__(self):
        super().__init__(10, 10, "MakeYou")

    def setup(self):
        """设置一个需要让其它物体成为 YOU 的关卡。"""
        # Place walls
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

    # 放置水平墙体作为障碍
        for x in range(1, self.width - 1):
            if x != 5:  # Leave gap
                wall = self.registry.create_instance("wall")
                self.grid.place_object(wall, x, 5)

    # 障碍下方放置 Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 5, 7)

    # 障碍上方放置 rock
        rock = self.registry.create_instance("rock")
        self.grid.place_object(rock, 5, 3)

    # 障碍上方放置旗帜
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 7, 2)

    # BABA IS YOU（可被破坏）
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 2, 7)
        self.grid.place_object(is_text, 3, 7)
        self.grid.place_object(you_text, 4, 7)

    # ROCK IS（未完成——需补上 YOU）
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)

        self.grid.place_object(rock_text, 6, 7)
        self.grid.place_object(is_text2, 7, 7)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 2, 2)
        self.grid.place_object(is_text3, 3, 2)
        self.grid.place_object(win_text, 4, 2)

        # WALL IS STOP
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 1, 1)
        self.grid.place_object(is_text4, 2, 1)
        self.grid.place_object(stop_text, 3, 1)


class TransformPuzzleEnvironment(Environment):
    """需要通过物体变形来取胜的环境。"""

    def __init__(self):
        super().__init__(10, 10, "TransformPuzzle")

    def setup(self):
        """设置一个变形类谜题。"""
        # Place walls
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

    # 放置水体作为屏障
        for x in range(3, 7):
            water = self.registry.create_instance("water")
            self.grid.place_object(water, x, 5)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 7)

    # 放置石头（用于变形）
        rock1 = self.registry.create_instance("rock")
        self.grid.place_object(rock1, 4, 7)

        rock2 = self.registry.create_instance("rock")
        self.grid.place_object(rock2, 5, 7)

    # 放置旗帜（初始不可达）
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 5, 2)

        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 5, 1)
        self.grid.place_object(is_text2, 6, 1)
        self.grid.place_object(win_text, 7, 1)

        # WATER IS SINK
        water_text = self.registry.create_instance("water", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        sink_text = self.registry.create_instance("sink", is_text=True)

        self.grid.place_object(water_text, 1, 8)
        self.grid.place_object(is_text3, 2, 8)
        self.grid.place_object(sink_text, 3, 8)

        # ROCK IS (incomplete - need BABA for transformation)
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)

        self.grid.place_object(rock_text, 6, 8)
        self.grid.place_object(is_text4, 7, 8)

    # 额外的 BABA 文字用于变形
        baba_text2 = self.registry.create_instance("baba", is_text=True)
        self.grid.place_object(baba_text2, 8, 7)


class MultiRuleEnvironment(Environment):
    """包含多条相互作用规则的环境。"""

    def __init__(self):
        super().__init__(12, 10, "MultiRule")

    def setup(self):
        """设置具有多重规则交互的关卡。"""
        # Place walls
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

    # 用墙体创建分区
        for y in range(1, 9):
            wall = self.registry.create_instance("wall")
            self.grid.place_object(wall, 4, y)
            wall2 = self.registry.create_instance("wall")
            self.grid.place_object(wall2, 8, y)

    # 在各分区放置物体
    # 左区：Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 5)

    # 中区：Rock 与 Water
        rock = self.registry.create_instance("rock")
        self.grid.place_object(rock, 6, 3)

        water = self.registry.create_instance("water")
        self.grid.place_object(water, 6, 6)

    # 右区：Flag
        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 10, 5)

    # 左区规则
        # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 2)
        self.grid.place_object(is_text, 2, 2)
        self.grid.place_object(you_text, 3, 2)

    # 中区规则
        # ROCK IS PUSH
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        push_text = self.registry.create_instance("push", is_text=True)

        self.grid.place_object(rock_text, 5, 2)
        self.grid.place_object(is_text2, 6, 2)
        self.grid.place_object(push_text, 7, 2)

    # WATER IS（未完成）
        water_text = self.registry.create_instance("water", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)

        self.grid.place_object(water_text, 5, 7)
        self.grid.place_object(is_text3, 6, 7)

    # 右区规则
        # FLAG IS WIN
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)
        win_text = self.registry.create_instance("win", is_text=True)

        self.grid.place_object(flag_text, 9, 2)
        self.grid.place_object(is_text4, 10, 2)
        self.grid.place_object(win_text, 11, 2)

    # 散落的规则碎片
        stop_text = self.registry.create_instance("stop", is_text=True)
        self.grid.place_object(stop_text, 2, 7)

        sink_text = self.registry.create_instance("sink", is_text=True)
        self.grid.place_object(sink_text, 10, 7)

    # WALL IS STOP（固定）
        wall_text = self.registry.create_instance("wall", is_text=True)
        is_text5 = self.registry.create_instance("is", is_text=True)
        stop_text2 = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(wall_text, 1, 1)
        self.grid.place_object(is_text5, 2, 1)
        self.grid.place_object(stop_text2, 3, 1)


class RuleChainEnvironment(Environment):
    """需要进行一系列规则操作的环境。"""

    def __init__(self):
        super().__init__(11, 9, "RuleChain")

    def setup(self):
        """设置需要顺序修改规则的关卡。"""
        # Place walls
        for x in range(self.width):
            wall_top = self.registry.create_instance("wall")
            wall_bottom = self.registry.create_instance("wall")
            self.grid.place_object(wall_top, x, 0)
            self.grid.place_object(wall_bottom, x, self.height - 1)

        for y in range(1, self.height - 1):
            wall_left = self.registry.create_instance("wall")
            wall_right = self.registry.create_instance("wall")
            self.grid.place_object(wall_left, 0, y)
            self.grid.place_object(wall_right, self.width - 1, y)

        # Place Baba
        baba = self.registry.create_instance("baba")
        self.grid.place_object(baba, 2, 4)

    # 按序放置物体
        rock = self.registry.create_instance("rock")
        self.grid.place_object(rock, 5, 4)

        water = self.registry.create_instance("water")
        self.grid.place_object(water, 7, 4)

        flag = self.registry.create_instance("flag")
        self.grid.place_object(flag, 9, 4)

    # 初始规则
    # BABA IS YOU
        baba_text = self.registry.create_instance("baba", is_text=True)
        is_text = self.registry.create_instance("is", is_text=True)
        you_text = self.registry.create_instance("you", is_text=True)

        self.grid.place_object(baba_text, 1, 1)
        self.grid.place_object(is_text, 2, 1)
        self.grid.place_object(you_text, 3, 1)

    # ROCK IS STOP
        rock_text = self.registry.create_instance("rock", is_text=True)
        is_text2 = self.registry.create_instance("is", is_text=True)
        stop_text = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(rock_text, 1, 2)
        self.grid.place_object(is_text2, 2, 2)
        self.grid.place_object(stop_text, 3, 2)

    # WATER IS STOP
        water_text = self.registry.create_instance("water", is_text=True)
        is_text3 = self.registry.create_instance("is", is_text=True)
        stop_text2 = self.registry.create_instance("stop", is_text=True)

        self.grid.place_object(water_text, 5, 1)
        self.grid.place_object(is_text3, 6, 1)
        self.grid.place_object(stop_text2, 7, 1)

    # FLAG IS（未完成）
        flag_text = self.registry.create_instance("flag", is_text=True)
        is_text4 = self.registry.create_instance("is", is_text=True)

        self.grid.place_object(flag_text, 9, 1)
        self.grid.place_object(is_text4, 10, 1)

    # 散落的规则碎片
        push_text = self.registry.create_instance("push", is_text=True)
        self.grid.place_object(push_text, 3, 6)

        win_text = self.registry.create_instance("win", is_text=True)
        self.grid.place_object(win_text, 8, 7)

        sink_text = self.registry.create_instance("sink", is_text=True)
        self.grid.place_object(sink_text, 5, 7)

    # 额外的 IS
        is_text5 = self.registry.create_instance("is", is_text=True)
        self.grid.place_object(is_text5, 6, 6)


"""
# 全部环境的注册表
"""
ENVIRONMENTS = {
    # 基础环境
    "simple": SimpleEnvironment,
    "wall_maze": WallMazeEnvironment,
    "push_puzzle": PushPuzzleEnvironment,
    "transformation": TransformationEnvironment,
    # 扩展环境
    "you_win": YouWinEnvironment,
    "make_win": MakeWinEnvironment,
    "two_room": TwoRoomEnvironment,
    "two_room_break_stop": TwoRoomBreakStopEnvironment,
    "make_win_distr": MakeWinWithDistractorsEnvironment,
    "goto_win_color": GotoWinWithColorEnvironment,
    # 进阶环境
    "make_you": MakeYouEnvironment,
    "transform_puzzle": TransformPuzzleEnvironment,
    "multi_rule": MultiRuleEnvironment,
    "rule_chain": RuleChainEnvironment,
}


def create_environment(name: str) -> Environment | None:
    """
    通过名称创建环境。

    参数：
        name: 环境名称

    返回：
        找到则返回环境实例，否则返回 None
    """
    env_class = ENVIRONMENTS.get(name.lower())
    if env_class:
        return env_class()
    return None


def list_environments() -> list[str]:
    """获取可用的环境名称列表。"""
    return list(ENVIRONMENTS.keys())
