"""
Baba Is You 的关卡环境。

本模块现仅保留一个用于加载官方关卡的环境：OfficialLevelEnvironment。
它会从本地 `map/` 目录读取指定世界与关卡号的 .l / .ld 关卡文件。
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

        # 初始化关卡内容
        self.setup()
        # 放置完所有文字后需提取规则
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
        self.setup()
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
        won, lost = self.grid.step(action)

        reward = 0.0
        if won:
            reward = 1.0
        elif lost:
            reward = -1.0

        done = won or lost
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


class OfficialLevelEnvironment(Environment):
    """从本地 map 根目录加载特定关卡（平铺式）。

    指定方式：
    - level_name: 如 "1level"、"n1level"（自动补 .l/.ld）
    - level_file: 关卡 .l 文件的路径（相对或绝对）
    """

    def __init__(
        self,
        *,
        level_name: str | None = None,
        level_file: str | Path | None = None,
        map_dir: str = "map",
    ):
        self.level_name = level_name
        self.level_file = Path(level_file) if level_file else None
        self.map_dir = map_dir

        title = Path(level_file).name if level_file else (level_name or "level")
        super().__init__(width=12, height=12, name=title)

    def setup(self):
        loader = LevelLoader(worlds_path=Path(self.map_dir))

        grid = None
        # 1) 明确给了 level_file：允许绝对或相对路径
        if self.level_file is not None:
            # 若给了绝对路径，覆写 loader 跟路径
            lfile = self.level_file
            base = lfile.parent
            name = lfile.stem
            temp_loader = LevelLoader(worlds_path=base)
            grid = temp_loader.load_level_flat(name, self.registry)
        # 2) 平铺名
        elif self.level_name is not None:
            grid = loader.load_level_flat(self.level_name, self.registry)

        if grid is None:
            # 加载失败则创建一个简单提示关卡
            self.grid = Grid(self.width, self.height, self.registry)
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
            # 更新标题
            self.name = f"{self.level_name or (self.level_file and Path(self.level_file).name) or 'level'} (fallback)"
        else:
            self.grid = grid
            self.width = grid.width
            self.height = grid.height


"""
# 本模块现仅保留用于官方关卡加载的环境：OfficialLevelEnvironment。
"""
