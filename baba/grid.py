"""Baba Is You 的主游戏网格与环境实现。"""

import copy

import cv2
import numpy as np

from .registration import Registry
from .rule import Property, RuleExtractor, RuleManager
from .world_object import Object


class Grid:
    """
    负责管理物体、规则与游戏状态的主游戏网格。

    核心职责：
    - 在每个位置存放物体（同一格可堆叠多个物体）
    - 管理由文字方块提取出的游戏规则
    - 处理物体移动、碰撞与变形
    - 追踪胜负状态
    - 负责渲染

    关键概念：
    - 网格坐标使用 [y][x]（行、列）索引
    - 同一位置可堆叠多个物体
    - 规则由横/竖排列且无间断的文字方块构成
    - 移动遵循 Baba Is You 的机制（PUSH、STOP 等）
    """

    def __init__(self, width: int, height: int, registry: Registry):
        """
        初始化网格。

        参数：
            width: 网格宽度
            height: 网格高度
            registry: 物体注册表
        """
        self.width = width
        self.height = height
        self.registry = registry

    # 网格在每个位置存放一个对象集合
    # 每个格子为一个 set，允许堆叠多个物体
    # 采用行优先的 grid[y][x] 索引
        self.grid: list[list[set[Object]]] = [[set() for _ in range(width)] for _ in range(height)]

    # 规则管理组件
    # RuleExtractor：扫描网格中文字以形成规则（如 BABA IS YOU）
    # RuleManager：存储激活的规则并提供属性查询
        self.rule_extractor = RuleExtractor(registry)
        self.rule_manager = RuleManager()

        # 游戏状态追踪
        self.won = False  # 当任一 YOU 物体触碰 WIN 物体时为 True
        self.lost = False  # 当不存在 YOU 物体时为 True
        self.steps = 0  # 累计步数

        # 初始更新规则
        self._update_rules()

    def place_object(self, obj: Object, x: int, y: int):
        """
        在指定位置放置一个物体。

        参数：
            obj: 要放置的物体
            x, y: 网格坐标
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].add(obj)

    def remove_object(self, obj: Object, x: int, y: int):
        """
        在指定位置移除一个物体。

        参数：
            obj: 要移除的物体
            x, y: 网格坐标
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].discard(obj)

    def get_objects_at(self, x: int, y: int) -> set[Object]:
        """
        获取某位置上的全部物体。

        参数：
            x, y: 网格坐标

        返回：
            该位置上的物体集合
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x].copy()
        return set()

    def move_object(self, obj: Object, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """
        将物体从一个位置移动到另一个位置。

        参数：
            obj: 要移动的物体
            from_x, from_y: 当前坐标
            to_x, to_y: 目标坐标

        返回：
            若移动成功返回 True
        """
        if not (0 <= to_x < self.width and 0 <= to_y < self.height):
            return False

        self.remove_object(obj, from_x, from_y)
        self.place_object(obj, to_x, to_y)
        return True

    def find_objects(
        self, obj_type: Object | None = None, name: str | None = None
    ) -> list[tuple[Object, int, int]]:
        """
        查找指定类型或名称的所有物体。

        参数：
            obj_type: 要查找的物体类型
            name: 要查找的物体名称

        返回：
            (object, x, y) 元组列表
        """
        results = []
        for y in range(self.height):
            for x in range(self.width):
                for obj in self.grid[y][x]:
                    if (
                        obj_type
                        and obj.type_id == obj_type.type_id
                        or name
                        and obj.name.upper() == name.upper()
                        or not obj_type
                        and not name
                    ):
                        results.append((obj, x, y))
        return results

    def step(self, action: str) -> tuple[bool, bool]:
        """
        按给定动作执行一步游戏逻辑。

        步骤顺序：
        1. 按方向移动所有具有 YOU 属性的物体
        2. 重新从文字提取规则（移动可能改变了规则）
        3. 应用变形（例如 ROCK IS BABA）
        4. 检查胜/负
        5. 处理 SINK 交互（销毁重叠的物体）

        参数：
            action: 'up' | 'down' | 'left' | 'right' | 'wait'

        返回：
            (won, lost) 元组表示游戏状态
        """
        self.steps += 1

        # Get movement direction
        dx, dy = 0, 0
        if action == "up":
            dx, dy = 0, -1
        elif action == "down":
            dx, dy = 0, 1
        elif action == "left":
            dx, dy = -1, 0
        elif action == "right":
            dx, dy = 1, 0

        # 移动所有具有 YOU 属性的物体
        # 注意：所有 YOU 物体同时移动
        if dx != 0 or dy != 0:
            you_objects = self.rule_manager.get_you_objects()
            for obj_name in you_objects:
                # Find all instances of this object type
                for obj, x, y in self.find_objects(name=obj_name):
                    self._try_move(obj, x, y, x + dx, y + dy)

    # 移动后更新规则
        self._update_rules()

    # 应用变形
        self._apply_transformations()

    # 检查胜/负
        self._check_win_lose()

    # 处理下沉（SINK）
        self._handle_sinking()

        return self.won, self.lost

    def _try_move(self, obj: Object, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """
        尝试移动某物体，处理推动与阻挡逻辑。

        移动规则：
        - 不能移动进带 STOP 属性的物体
        - 带 PUSH 属性的物体若目的地有空位即可被推动
        - 文字方块永远可被推动
        - 推动链：被推动的物体可以继续推动其他物体

        本方法为递归实现以支持推动链。

        参数：
            obj: 要移动的物体
            from_x, from_y: 当前坐标
            to_x, to_y: 目标坐标

        返回：
            若移动成功返回 True
        """
        # Check bounds
        if not (0 <= to_x < self.width and 0 <= to_y < self.height):
            return False

    # 检查目标位置上的内容
        target_objects = self.get_objects_at(to_x, to_y)

        # 检查 STOP 属性——会阻挡一切移动
        for target_obj in target_objects:
            if self.rule_manager.has_property(target_obj.name, Property.STOP):
                return False

        # 收集目标位置上可推动的物体
        # 带 PUSH 属性的物体与所有文字方块均可推动
        push_objects = []
        for target_obj in target_objects:
            if self.rule_manager.has_property(target_obj.name, Property.PUSH) or target_obj.is_text:
                push_objects.append(target_obj)

        # 如存在可推动物体，则尝试推动它们
        if push_objects:
            # Calculate where to push objects (same direction)
            dx = to_x - from_x
            dy = to_y - from_y
            push_to_x = to_x + dx
            push_to_y = to_y + dy

            # 所有被推动物体都必须能移动，推动才算成功
            # 这会形成推动链（物体推动物体）
            for push_obj in push_objects:
                if not self._try_move(push_obj, to_x, to_y, push_to_x, push_to_y):
                    return False

    # 移动有效，执行移动
        self.move_object(obj, from_x, from_y, to_x, to_y)
        return True

    def _update_rules(self):
        """
        从网格中提取并更新激活的规则。

        规则由以下模式的文字方块组成：
        - NOUN IS PROPERTY（如 BABA IS YOU）
        - NOUN IS NOUN（如 ROCK IS BABA）

        文本需水平或垂直连续对齐且无间隔。
        """
        rules = self.rule_extractor.extract_rules(self.grid)
        self.rule_manager.update_rules(rules)

    def _apply_transformations(self):
        """
        根据激活规则应用物体变形。

        当存在类似 "ROCK IS BABA" 的规则时，所有 ROCK 物体会立刻变为 BABA。

        注意：文字方块不会发生变形。
        """
        transformations = []

        # 收集所有需要变形的项
        for y in range(self.height):
            for x in range(self.width):
                for obj in list(self.grid[y][x]):  # Copy to avoid modification during iteration
                    transform_to = self.rule_manager.get_transformation(obj.name)
                    if transform_to:
                        # Find the target object type
                        target_obj = self.registry.get_object(transform_to.lower())
                        if target_obj:
                            transformations.append((obj, x, y, target_obj))

        # 应用变形
        for obj, x, y, new_obj in transformations:
            self.remove_object(obj, x, y)
            # Create a new instance of the target object
            new_instance = copy.deepcopy(new_obj)
            self.place_object(new_instance, x, y)

    def _check_win_lose(self):
        """
        检查胜/负条件。

        胜利：任一 YOU 物体与任一 WIN 物体重叠
        失败：不存在具有 YOU 属性的物体

        注意：一旦设置了胜/负标记，将在重置前保持。
        """
        you_objects = self.rule_manager.get_you_objects()
        win_objects = self.rule_manager.get_win_objects()

        if not you_objects:
            self.lost = True
            return

        # 检查是否有 YOU 物体处于 WIN 物体所在位置
        for you_name in you_objects:
            for you_obj, you_x, you_y in self.find_objects(name=you_name):
                # Check all objects at the same position
                for other_obj in self.get_objects_at(you_x, you_y):
                    if other_obj != you_obj and other_obj.name.upper() in win_objects:
                        self.won = True
                        return

    def _handle_sinking(self):
        """
        处理 SINK 属性的交互。

        具有 SINK 的物体会摧毁其所在位置的所有物体（包括自身）。
        该处理发生在移动之后。
        """
        sink_objects = self.rule_manager.get_sink_objects()

        # 找出所有包含 SINK 物体的位置
        sink_positions = []
        for sink_name in sink_objects:
            for _, x, y in self.find_objects(name=sink_name):
                sink_positions.append((x, y))

        # 清空这些位置上的所有物体
        for x, y in sink_positions:
            self.grid[y][x].clear()

    def render(self, cell_size: int = 24) -> np.ndarray:
        """
        将网格渲染为图像。

        参数：
            cell_size: 每格像素大小

        返回：
            渲染后的 numpy 数组
        """
        # Create dark background
        img = np.full(
            (self.height * cell_size, self.width * cell_size, 3), (20, 20, 20), dtype=np.uint8
        )

        # Add subtle grid lines
        grid_color = (35, 35, 35)
        for y in range(0, self.height * cell_size, cell_size):
            img[y : y + 1, :] = grid_color
        for x in range(0, self.width * cell_size, cell_size):
            img[:, x : x + 1] = grid_color

        # Render each cell
        for y in range(self.height):
            for x in range(self.width):
                objects = self.grid[y][x]
                if objects:
                    # Render the top object (text renders above regular objects)
                    # Sort by: text objects first, then by type_id for consistency
                    obj = max(objects, key=lambda o: (o.is_text, o.type_id))
                    sprite = obj.render((cell_size, cell_size))

                    # Place sprite in image
                    y_start = y * cell_size
                    x_start = x * cell_size
                    img[y_start : y_start + cell_size, x_start : x_start + cell_size] = sprite

                    # 若同格有多个物体，添加角标提示
                    if len(objects) > 1:
                        # 在角落画一个小白点表示堆叠
                        cv2.circle(
                            img, (x_start + cell_size - 4, y_start + 4), 2, (255, 255, 255), -1
                        )

        return img

    def get_state(self) -> np.ndarray:
        """
        以 3D 数组形式导出当前状态，便于 AI Agent 使用。

        在每个位置编码物体的类型 ID，最多记录每格的若干个物体。

        返回：
            形状为 (height, width, max_objects_per_cell) 的数组
        """
        max_objects_per_cell = 3  # Adjust as needed
        state = np.zeros((self.height, self.width, max_objects_per_cell), dtype=np.int32)

        for y in range(self.height):
            for x in range(self.width):
                objects = list(self.grid[y][x])
                for i, obj in enumerate(objects[:max_objects_per_cell]):
                    state[y, x, i] = obj.type_id

        return state

    def reset(self):
        """将网格重置为空状态。"""
        self.grid = [[set() for _ in range(self.width)] for _ in range(self.height)]
        self.won = False
        self.lost = False
        self.steps = 0
        self._update_rules()

    def copy(self) -> "Grid":
        """创建该网格的深拷贝。"""
        new_grid = Grid(self.width, self.height, self.registry)

        # Copy all objects
        for y in range(self.height):
            for x in range(self.width):
                for obj in self.grid[y][x]:
                    new_obj = copy.deepcopy(obj)
                    new_grid.place_object(new_obj, x, y)

        # Copy game state
        new_grid.won = self.won
        new_grid.lost = self.lost
        new_grid.steps = self.steps

        # Update rules in the new grid
        new_grid._update_rules()

        return new_grid
