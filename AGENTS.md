# AGENTS.md

## 仓库定位

本仓库面向单篇数据驱动、过程密集型定量科学研究。
一个仓库默认对应一篇论文或一项完整定量分析。

## 任务入口

- 开始任何任务前先读 `README.md` 和 `DASHBOARD.md`。
- 根目录存在 `INITIALIZE_PROJECT.md` 时，项目尚未完成初始化；优先按该清单执行，完成后删除它。
- Titanic 三阶段示例只从 `docs/examples/titanic-walkthrough.md` 进入，不把示例分支整体合并或拣选到新项目。

## 按任务读取

- 数据任务：`data/README.md`、`docs/data-sources.md`、`docs/workflows/data-lifecycle.md`。
- 研究步骤：`src/README.md`、`README.md` 的“研究执行顺序”、`docs/workflows/research-execution.md`。
- 实验任务：`experiments/README.md`、`docs/workflows/experiments.md`。
- 写作任务：`docs/writing/README.md`、`docs/writing/manuscript/README.md`、`docs/workflows/manuscript.md`、`docs/workflows/writing-and-figures.md`。
- 协作任务：`docs/workflows/collaboration.md`。

## 全局规则

- `DASHBOARD.md` 是项目状态的唯一真源。
- `outputs/figures/` 和 `outputs/tables/` 是正式图件和表格的唯一真源。
- 不覆盖 `data/raw/` 中的原始数据；非显然转换必须可追溯。
- 根 `README.md` 中人工维护的执行顺序是完整命令、输入、输出和依赖关系的权威说明。
- 不建立一键运行全部研究的总控入口，不默认引入工作流引擎。
- 不擅自建立 Notebook、subagent、MCP、provider、model、sandbox 配置或大量 skills。
- `.agents/skills/example-skill/` 只是格式示例，不是默认工作流。
- 使用 `uv` 管理 Python 依赖；不手工编辑 `uv.lock`。
- 文档默认使用中文；代码、命令、路径和技术标识符保留英文。

## Git 安全

- 非平凡修改前执行 `git fetch origin`、`git status --short --branch` 和 `git rev-list --left-right --count HEAD...@{u}`。
- 本地落后上游时先停下，不自行 merge、rebase 或改写历史。
- 已有工作区改动视为用户改动；不使用 `reset --hard`、`checkout --`、`restore` 或自动 stash 丢弃它们。
- 显式选择提交文件；不提交凭据、大型原始数据或无关改动；不 force push。

## 完成前最低验证

- 从 `README.md` 列出的命令逐项验证受影响步骤。
- 运行 `git diff --check`，并对变更的 shell、Python、TeX 文件执行相应语法或构建检查。
- 确认正式输出、生成脚本、输入和关键参数可以互相追溯。
- 状态或结果变化时同步更新 `DASHBOARD.md`、相关实验 README 和执行顺序。
