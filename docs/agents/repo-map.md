# 仓库结构

## 根目录

- `README.md`: 项目定位与快速开始。
- `AGENTS.md`: 运行规则。
- `DASHBOARD.md`: 进度看板。
- `Makefile`: 常用命令。
- `pyproject.toml`: 依赖与基础配置。
- `scripts/`: 初始化与脚本工具。
- `src/`: 数据处理与可复用逻辑。
- `notebooks/`: 交互式探索。
- `experiments/`: 可复现实验。
- `outputs/`: 图表和表格输出。
- `docs/`: 流程与写作文档。

## 约定目录

- `data/raw`, `data/interim`, `data/processed`, `data/external`: 数据分层。
- `docs/plans/`: 研究计划和阶段性计划。
- `docs/project-preferences.md`: 环境、工具和操作偏好。
- `docs/agents/dbschema/`: 数据库 schema 文档。
- `docs/writing/manuscript/`: TeX 写作主工作区。
- `.agents/skills/`: Codex skill。
- `.codex/agents/`: 自定义 Codex agent。
- `.codex/config.toml`: 项目级配置。
- `.claude/` 与 `CLAUDE.md`: 兼容层。
