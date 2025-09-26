"""
Baba Is You 的 Agent 接口，内置了回合（Episode）运行功能。

Agent 只需实现 get_action(observation) 即可工作。
基类提供了 play_episode() 与 play_episodes() 便捷方法。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pygame
from PIL import Image

from .grid import Grid


class Agent(ABC):
    """
    Baba Is You Agent 的抽象基类。

    子类只需实现 get_action(observation)。
    基类提供了便捷的方法用于运行回合。
    """

    def __init__(self, name: str = "Agent"):
        """使用名称初始化 Agent。"""
        self.name = name

    @abstractmethod
    def get_action(self, observation: Grid) -> str:
        """
        根据当前观测选择一个动作。

        参数：
            observation: 当前游戏状态（Grid 对象）

        返回：
            动作字符串：取值为 ["up", "down", "left", "right", "wait"] 之一
        """
        pass

    def reset(self):  # noqa: B027
        """
        为新回合重置 Agent。

        如果 Agent 维护内部状态，可在子类中覆盖。
        """
        pass

    def play_episode(
        self,
        env,
        render: bool = False,
        record: bool = False,
        record_path: str | None = None,
        cell_size: int = 48,
        fps: int = 30,
        verbose: bool = True,
        max_steps: int = 200,
    ) -> dict:
        """
        在给定环境中运行单次回合。

        参数：
            env: 要游玩的环境
            render: 是否进行可视化渲染
            record: 是否将回合录制为 GIF
            record_path: 录制保存路径（为 None 时自动生成）
            cell_size: 渲染时每个格子的像素大小
            fps: 渲染帧率
            verbose: 是否打印回合信息
            max_steps: 强制结束回合的最大步数

        返回：
            包含回合统计信息的字典
        """
        # 若启用渲染则初始化 pygame
        screen = None
        clock = None
        font = None
        frames = []

        if render:
            pygame.init()
            width = env.width * cell_size
            height = env.height * cell_size + 120  # 为展示推理 UI 预留额外空间
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(f"Baba Is You - {env.name} ({self.name})")
            clock = pygame.time.Clock()
            font = pygame.font.Font(None, 24)

        # 重置环境与 Agent
        obs = env.reset()
        self.reset()

        if verbose:
            print(f"\n=== Playing {env.name} with {self.name} ===")

        # 回合主循环
        done = False
        total_reward = 0.0
        steps = 0
        start_time = pygame.time.get_ticks() if render else 0

        while not done and steps < max_steps:
            # 如启用渲染则绘制一帧
            if render:
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
                self._render_frame(screen, env, obs, font, cell_size, elapsed_time)
                if record:
                    frames.append(self._capture_frame(screen))
                clock.tick(fps)

                # 处理 pygame 事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        break

            # 从 Agent 获取动作
            action = self.get_action(obs)

            # 在环境中执行动作
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1

            if verbose and done:
                if info["won"]:
                    print(f"🎉 Won in {info['steps']} steps!")
                elif info["lost"]:
                    print(f"💀 Lost after {info['steps']} steps")

            # 检查是否达到步数上限
            if steps >= max_steps and not done:
                done = True
                info["timeout"] = True
                if verbose:
                    print(f"⏱️ Timeout after {max_steps} steps")

        # 如开启录制则保存 GIF
        if record and frames:
            self._save_recording(frames, record_path, env, fps, verbose)

        # 清理 pygame
        if render:
            pygame.quit()

        # 返回回合统计
        return {
            "won": info.get("won", False),
            "lost": info.get("lost", False),
            "steps": info.get("steps", steps),
            "reward": total_reward,
            "timeout": info.get("timeout", False),
        }

    def play_episodes(
        self, env, num_episodes: int = 1, render: bool = False, verbose: bool = True, **kwargs
    ) -> dict:
        """
        运行多次回合并返回聚合统计。

        参数：
            env: 要游玩的环境
            num_episodes: 回合次数
            render: 是否可视化渲染
            verbose: 是否打印信息
            **kwargs: 传递给 play_episode() 的其他参数

        返回：
            聚合统计字典
        """
        stats = {
            "episodes": num_episodes,
            "wins": 0,
            "losses": 0,
            "total_steps": 0,
            "total_reward": 0.0,
            "win_rate": 0.0,
            "avg_steps": 0.0,
            "avg_reward": 0.0,
        }

        for i in range(num_episodes):
            if verbose and num_episodes > 1:
                print(f"\n--- Episode {i + 1}/{num_episodes} ---")

            episode_stats = self.play_episode(env, render=render, verbose=verbose, **kwargs)

            # Update statistics
            if episode_stats["won"]:
                stats["wins"] += 1
            elif episode_stats["lost"]:
                stats["losses"] += 1
            stats["total_steps"] += episode_stats["steps"]
            stats["total_reward"] += episode_stats["reward"]

        # 计算均值
        stats["win_rate"] = stats["wins"] / num_episodes if num_episodes > 0 else 0.0
        stats["avg_steps"] = stats["total_steps"] / num_episodes if num_episodes > 0 else 0.0
        stats["avg_reward"] = stats["total_reward"] / num_episodes if num_episodes > 0 else 0.0

        # 打印汇总
        if verbose and num_episodes > 1:
            print("\n=== Episode Summary ===")
            print(f"Total episodes: {num_episodes}")
            print(f"Wins: {stats['wins']} ({stats['win_rate']*100:.1f}%)")
            print(f"Losses: {stats['losses']}")
            print(f"Average steps: {stats['avg_steps']:.1f}")
            print(f"Average reward: {stats['avg_reward']:.2f}")

        return stats

    def _render_frame(
        self, screen, env, obs: Grid, font, cell_size: int, elapsed_time: float = 0.0
    ):
        """渲染一帧画面。"""
        # Clear screen
        screen.fill((0, 0, 0))

        # 渲染网格
        grid_image = env.render("rgb_array", cell_size)
        grid_surface = pygame.surfarray.make_surface(grid_image.swapaxes(0, 1))
        screen.blit(grid_surface, (0, 0))

        # 渲染 UI
        y_offset = env.height * cell_size + 10

        # 状态文本
        if obs.won:
            status_text = "YOU WIN!"
            color = (0, 255, 0)
        elif obs.lost:
            status_text = "YOU LOSE!"
            color = (255, 0, 0)
        else:
            status_text = f"Steps: {obs.steps} | Time: {elapsed_time:.1f}s"
            color = (255, 255, 255)

        status_text += f" | Agent: {self.name}"
        status_surface = font.render(status_text, True, color)
        screen.blit(status_surface, (10, y_offset))

        # 若可用，显示 Agent 的“思考”
        if hasattr(self, "last_reasoning"):
            reasoning_text = f"Thinking: {self.last_reasoning}"
            reasoning_surface = font.render(reasoning_text, True, (255, 255, 100))
            screen.blit(reasoning_surface, (10, y_offset + 25))
            rules_y_offset = y_offset + 50
        else:
            rules_y_offset = y_offset + 30

        # 显示部分规则
        rules = obs.rule_manager.rules[:4]
        if rules:
            rules_text = "Rules: " + ", ".join(str(rule) for rule in rules)
            if len(obs.rule_manager.rules) > 4:
                rules_text += f" (+{len(obs.rule_manager.rules) - 4} more)"
            rules_surface = font.render(rules_text, True, (150, 150, 255))
            screen.blit(rules_surface, (10, rules_y_offset))

        pygame.display.flip()

    def _capture_frame(self, screen) -> Image.Image:
        """将当前屏幕捕获为 PIL Image。"""
        frame_str = pygame.image.tostring(screen, "RGB")
        width, height = screen.get_size()
        return Image.frombytes("RGB", (width, height), frame_str)

    def _save_recording(self, frames: list, record_path: str | None, env, fps: int, verbose: bool):
        """将帧保存为动图 GIF。"""
        if not frames:
            return

        # 确定输出路径
        if record_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            record_path = f"recordings/{env.name}_{self.name.replace(' ', '_')}_{timestamp}.gif"

        # 确保目录存在
        Path(record_path).parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Saving recording to {record_path}...")

        # 保存 GIF
        duration_ms = int(1000 / fps)
        frames[0].save(
            record_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

        if verbose:
            size_kb = Path(record_path).stat().st_size / 1024
            print(f"Recording saved! {len(frames)} frames, {size_kb:.1f} KB")


class UserAgent(Agent):
    """
    人类玩家 Agent，从键盘输入获取动作。

    操作：
    - 方向键或 WASD：移动
    - 空格：等待
    - Q/ESC：退出（由 play_episode 处理）
    """

    def __init__(self):
        super().__init__("Human Player")

    def get_action(self, observation: Grid) -> str:  # noqa: ARG002
        """
        从键盘输入获取动作。

        返回：
            动作字符串
        """
        # 等待键盘输入
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 移动按键
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        return "up"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        return "down"
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        return "left"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        return "right"
                    elif event.key == pygame.K_SPACE:
                        return "wait"

            # 小延时避免 CPU 飙高
            pygame.time.wait(10)
