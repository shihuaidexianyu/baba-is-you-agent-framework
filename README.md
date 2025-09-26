# Baba Is You Agent Framework（精简版）

```text
baba-is-agi/
├── baba/                 # 核心游戏实现
│   ├── grid.py           # 游戏网格与主逻辑
│   ├── world_object.py   # 游戏对象与文字块
│   ├── rule.py           # 规则解析与管理
│   ├── properties.py     # 游戏属性（YOU、WIN、STOP 等）
│   ├── rendering.py      # 基础渲染工具
│   ├── sprites.py        # 自定义 ASCII 精灵生成
│   ├── sprite_loader.py  # （若可用）加载官方精灵
│   ├── level_loader.py   # 加载官方关卡
│   ├── envs.py           # 所有关卡环境（共 14 个）
│   ├── agent.py          # 基础 Agent 类
│   └── assets/sprites/   # 官方游戏精灵目录（已在 gitignore 中忽略）
├── agents/               # Agent 实现
│   ├── random_agent.py   # 简单的随机 Agent
│   ├── demo_agent.py     # 贪心/广搜风格寻路 Agent
│   └── claude_code_agent.py # Claude API Agent
├── scripts/              # 实用脚本
├── tests/                # 完整测试集（102 个测试）
├── docs/                 # 文档
└── requirements.txt     # 依赖清单（pip 安装）
```

该仓库保留了用于实验所需的核心内容：Baba Is You 游戏引擎与两个基线 Agent（random 与 demo）。
安装与运行基于 `requirements.txt` 进行 pip 安装。

## 包含组件

- `baba/`：完整的游戏引擎、规则系统与内置谜题环境。
- `agents/random_agent.py`：极简基线，均匀采样动作。
- `agents/demo_agent.py`：确定性的“广度优先风格”求解器，懂得推动物体。
- `requirements.txt`：安装与运行引擎/Agent 的依赖清单。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 运行游戏引擎

平铺式关卡（map 根目录）：

列出：

```bash
python -m baba.play --list-levels --map-dir map
```

游玩：

```bash
python -m baba.play --level-name 1level --map-dir map
# 或指定文件
python -m baba.play --level-file map/1level.l
```

操作：方向键或 WASD 移动，`R` 重开关卡，`Q` 退出。

## 基线 Agent

随机 Agent：

```bash
python agents/random_agent.py
```

带寻路的 Demo Agent：

```bash
python agents/demo_agent.py
```

上述脚本通过 `LEVEL_NAME` 或 `LEVEL_FILE` 环境变量选择关卡，例如：

```bash
LEVEL_NAME=1level python agents/random_agent.py
# 或
LEVEL_FILE=map/1level.l python agents/demo_agent.py
```

## 目录结构

```text
baba-is-you-agent-framework/
├── baba/            # 核心引擎与环境
├── agents/
│   ├── demo_agent.py
│   └── random_agent.py
├── requirements.txt
└── README.md
```

## 说明

- 引擎支持官方 Baba Is You 的关卡格式（需自备 `map/` 文件）。
- 要构建自定义 Agent，实现 `baba.agent.Agent` 并像 demo 脚本那样调用 `play_episode()` 即可。

---

本仓库的文档与代码注释已本地化为中文；如需英文版，可通过 Git 历史查看早期提交。
