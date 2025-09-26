"""
Baba Is You 的游玩入口。

提供一个简单的交互式游玩接口。
若要使用 AI Agent，请参考 agents/ 目录中的脚本。
"""

import argparse
import sys

from .agent import UserAgent
from .envs import OfficialLevelEnvironment
from pathlib import Path


def play_official(world: str, level: int, map_dir: str = "map", cell_size: int = 48, fps: int = 30) -> dict:
    """从本地 map 目录加载并游玩指定官方关卡。"""
    env = OfficialLevelEnvironment(world=world, level=level, map_dir=map_dir)
    agent = UserAgent()
    return agent.play_episode(env=env, render=True, cell_size=cell_size, fps=fps, verbose=True)


def main():
    """用于游玩 Baba Is You 的命令行接口。"""
    parser = argparse.ArgumentParser(
        description="Play Baba Is You interactively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Play interactively (default)
  pixi run play

  # Play specific environment
  pixi run play --env push_puzzle

  # Play with larger cells
  pixi run play --cell-size 64

For AI agents, see the agents/ directory:
  python agents/random.py simple
  python agents/claude-code.py simple
""",
    )

    # 内置环境已移除，仅支持本地 map 目录的官方关卡

    parser.add_argument(
        "--cell-size",
        type=int,
        default=48,
        help="Size of each cell in pixels (default: 48)",
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)",
    )

    # 已移除 --list-envs

    # Official level loading from local 'map' folder
    parser.add_argument(
        "--map-dir",
        default="map",
        help="Directory containing official level worlds (default: ./map)",
    )
    parser.add_argument(
        "--world",
        help="World name to load from map directory (e.g., 'baba', 'new_adv')",
    )
    parser.add_argument(
        "--level",
        type=int,
        help="Level number within the world to load (e.g., 1, 2, 3)",
    )
    parser.add_argument(
        "--list-worlds",
        action="store_true",
        help="List available worlds in map directory and exit",
    )
    parser.add_argument(
        "--list-levels",
        metavar="WORLD",
        help="List available levels in the specified world and exit",
    )

    args = parser.parse_args()

    # 不再支持列出内置环境

    # Handle listing worlds/levels in map directory
    if args.list_worlds or args.list_levels:
        from .level_loader import LevelLoader

        loader = LevelLoader(worlds_path=Path(args.map_dir))
        if args.list_worlds:
            worlds = loader.list_worlds()
            if not worlds:
                print(f"No worlds found in {args.map_dir}")
            else:
                print("Worlds in map directory:")
                for w in worlds:
                    print(f"  - {w}")
            return 0
        if args.list_levels:
            worlds = loader.list_worlds()
            if args.list_levels not in worlds:
                print(f"World '{args.list_levels}' not found in {args.map_dir}")
                print("Available:")
                for w in worlds:
                    print(f"  - {w}")
                return 1
            levels = loader.list_levels(args.list_levels)
            print(f"Levels in world '{args.list_levels}':")
            for lv in levels:
                print(f"  - {lv}")
            return 0

    # Play the game
    try:
        # 仅支持 world+level 路径
        if not (args.world and args.level is not None):
            print("Please provide --world and --level to play an official level from the local map directory.")
            return 1
        play_official(world=args.world, level=args.level, map_dir=args.map_dir, cell_size=args.cell_size, fps=args.fps)
    except KeyboardInterrupt:
        print("\nGame interrupted by user")

    return 0


if __name__ == "__main__":
    sys.exit(main())
