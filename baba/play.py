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


def play_official_flat(level_name: str | None, level_file: str | None, map_dir: str = "map", cell_size: int = 48, fps: int = 30) -> dict:
    """从本地 map 根目录加载并游玩指定官方关卡（平铺）。"""
    env = OfficialLevelEnvironment(level_name=level_name, level_file=level_file, map_dir=map_dir)
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

    # Official level loading from local 'map' folder (flat layout)
    parser.add_argument(
        "--map-dir",
        default="map",
        help="Directory containing official levels (default: ./map)",
    )
    parser.add_argument(
        "--level-name",
        help="Level filename without extension in map dir (e.g., '1level', 'n1level')",
    )
    parser.add_argument(
        "--level-file",
        help="Path to a level .l file (absolute or relative)",
    )
    parser.add_argument(
        "--list-levels",
        action="store_true",
        help="List available levels in map directory and exit",
    )

    args = parser.parse_args()

    # 不再支持列出内置环境

    # Handle listing levels in flat map directory
    if args.list_levels:
        from .level_loader import LevelLoader

        loader = LevelLoader(worlds_path=Path(args.map_dir))
        names = loader.list_level_names()
        if not names:
            print(f"No levels found in {args.map_dir}")
        else:
            print("Levels in map directory:")
            for n in names:
                print(f"  - {n}")
        return 0

    # Play the game
    try:
        # 仅支持平铺：提供 --level-name 或 --level-file
        if not (args.level_name or args.level_file):
            print("Please provide --level-name (e.g., '1level') or --level-file (<path>.l)")
            return 1
        play_official_flat(level_name=args.level_name, level_file=args.level_file, map_dir=args.map_dir, cell_size=args.cell_size, fps=args.fps)
    except KeyboardInterrupt:
        print("\nGame interrupted by user")

    return 0


if __name__ == "__main__":
    sys.exit(main())
