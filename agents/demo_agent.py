#!/usr/bin/env python3
"""
用于 Baba Is You 的简单演示 Agent，可解基本关卡。
使用 BFS 寻路以到达 WIN 物体，并能处理可推动（PUSH）的物体。
"""

from collections import deque

from baba.agent import Agent
from baba.grid import Grid


class DemoAgent(Agent):
    """使用 BFS 寻路以接近 WIN 物体的 Agent。"""

    def __init__(self):
        super().__init__("Demo Agent")
        self.path_cache = {}  # 在不同回合之间缓存路径
        self.last_reasoning = ""  # 为空以保持 UI 一致（demo agent 不“思考”）

    def reset(self):
        """为新回合重置 Agent。"""
        self.path_cache = {}
        self.last_reasoning = ""  # 为空以保持 UI 一致

    def get_action(self, observation: Grid) -> str:
        """
        使用可处理可推动物体的简化寻路来选择动作。

        参数：
            observation: 当前游戏状态

        返回：
            要执行的动作
        """
        # 查找 YOU 与 WIN 物体
        you_objects = observation.rule_manager.get_you_objects()
        win_objects = observation.rule_manager.get_win_objects()

        if not you_objects:
            return "wait"  # 没有可控制的物体

        # 获取当前位置
        you_positions = self._find_you_positions(observation, you_objects)
        win_positions = self._find_win_positions(observation, win_objects)

        if not you_positions or not win_positions:
            return "wait"  # 找不到位置

        # 为简化起见，控制第一个 YOU 物体
        you_pos = you_positions[0]
        target_pos = win_positions[0]

        # 尝试具备推动意识的简化寻路
        action = self._simple_pathfind_with_push(observation, you_pos, target_pos)

        # 推理留空——演示 Agent 不“思考”
        self.last_reasoning = ""

        return action

    def _find_you_positions(self, observation: Grid, you_objects: set[str]) -> list:
        """找到所有可控制物体的位置。"""
        positions = []
        # 转小写以便比较
        you_objects_lower = {obj.lower() for obj in you_objects}
        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in you_objects_lower:
                        positions.append((x, y))
        return positions

    def _find_win_positions(self, observation: Grid, win_objects: set[str]) -> list:
        """找到所有胜利物体的位置。"""
        positions = []
        # 转小写以便比较
        win_objects_lower = {obj.lower() for obj in win_objects}
        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in win_objects_lower:
                        positions.append((x, y))
        return positions

    def _get_push_positions(self, observation: Grid) -> set[tuple[int, int]]:
        """获取所有可推动物体的位置。"""
        push_objects = observation.rule_manager.get_push_objects()
        # 转小写以便比较
        push_objects_lower = {obj.lower() for obj in push_objects}
        positions = set()

        for y in range(observation.height):
            for x in range(observation.width):
                for obj in observation.grid[y][x]:
                    if not obj.is_text and obj.name.lower() in push_objects_lower:
                        positions.add((x, y))

        return positions

    def _simple_pathfind_with_push(
        self, observation: Grid, start: tuple[int, int], goal: tuple[int, int]
    ) -> str:
        """
        简化寻路：在需要时尝试推动物体以抵达目标。
        使用局部 BFS 以寻找下一步动作。
        """
        # Get object types (convert to lowercase for comparison)
        push_objects = {obj.lower() for obj in observation.rule_manager.get_push_objects()}
        stop_objects = {obj.lower() for obj in observation.rule_manager.get_stop_objects()}

        # 局部 BFS（限制深度）
        queue = deque([(start, [], 0)])
        visited = {start}
        max_local_depth = 10  # Look ahead a few moves

        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

        while queue:
            pos, path, depth = queue.popleft()

            if depth > max_local_depth:
                continue

            # 检查是否已到达目标
            if pos == goal:
                return path[0] if path else "wait"

            # 尝试各个方向
            for action, (dx, dy) in directions.items():
                new_x = pos[0] + dx
                new_y = pos[1] + dy

                # 边界检查
                if (
                    new_x < 0
                    or new_x >= observation.width
                    or new_y < 0
                    or new_y >= observation.height
                ):
                    continue

                # 检查新位置的物体
                can_move = True

                for obj in observation.grid[new_y][new_x]:
                    if obj.is_text:
                        continue

                    # 检查是否为 STOP 物体
                    if obj.name in stop_objects:
                        # 若也可推动则尝试推动
                        if obj.name in push_objects:
                            # 检查是否能推动
                            push_x = new_x + dx
                            push_y = new_y + dy

                            # 推动后的边界检查
                            if (
                                push_x < 0
                                or push_x >= observation.width
                                or push_y < 0
                                or push_y >= observation.height
                            ):
                                can_move = False
                                break

                            # 检查推动目的地是否被阻塞
                            for push_obj in observation.grid[push_y][push_x]:
                                if not push_obj.is_text and push_obj.name in stop_objects:
                                    can_move = False
                                    break
                        else:
                            # STOP 且不可推动
                            can_move = False
                            break

                if can_move and (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append(((new_x, new_y), path + [action], depth + 1))

        # 若 BFS 未找到路径，则尝试直接的贪心策略
        return self._greedy_move_with_push(observation, start, goal)

    def _greedy_move_with_push(
        self, observation: Grid, you_pos: tuple[int, int], goal_pos: tuple[int, int]
    ) -> str:
        """考虑可推动性的贪心移动。"""
        you_x, you_y = you_pos
        goal_x, goal_y = goal_pos

        # 计算优先方向
        dx = goal_x - you_x
        dy = goal_y - you_y

        # 若横向距离更长，则优先尝试横向
        if abs(dx) >= abs(dy):
            if dx > 0:
                action = "right"
            elif dx < 0:
                action = "left"
            elif dy > 0:
                action = "down"
            elif dy < 0:
                action = "up"
            else:
                return "wait"
        else:
            if dy > 0:
                action = "down"
            elif dy < 0:
                action = "up"
            elif dx > 0:
                action = "right"
            elif dx < 0:
                action = "left"
            else:
                return "wait"

        # Check if this move is valid
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = directions[action]
        new_x = you_x + dx
        new_y = you_y + dy

        # 边界检查
        if new_x < 0 or new_x >= observation.width or new_y < 0 or new_y >= observation.height:
            return "wait"

        # 检查该移动是否有效（考虑推动）
        push_objects = {obj.lower() for obj in observation.rule_manager.get_push_objects()}
        stop_objects = {obj.lower() for obj in observation.rule_manager.get_stop_objects()}

        for obj in observation.grid[new_y][new_x]:
            if obj.is_text:
                continue

            if obj.name in stop_objects:
                if obj.name in push_objects:
                    # 可推动——检查推动是否有效
                    push_x = new_x + dx
                    push_y = new_y + dy

                    if (
                        push_x < 0
                        or push_x >= observation.width
                        or push_y < 0
                        or push_y >= observation.height
                    ):
                        return "wait"

                    # 检查推动目的地
                    for push_obj in observation.grid[push_y][push_x]:
                        if not push_obj.is_text and push_obj.name in stop_objects:
                            return "wait"
                else:
                    # 不可推动，被阻挡
                    return "wait"

        return action


# 示例用法
if __name__ == "__main__":
    import sys

    from baba import create_environment

    # 从命令行获取环境名或使用默认
    env_name = sys.argv[1] if len(sys.argv) > 1 else "simple"

    # 创建环境
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        sys.exit(1)

    # 创建 Agent 并开始游玩
    agent = DemoAgent()
    stats = agent.play_episode(env, render=True, verbose=True)

    print(f"\nFinal stats: {stats}")
