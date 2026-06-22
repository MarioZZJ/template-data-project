# AGENTS.md

## 目标

本仓库是可复现的数据/科研项目模板。

Agent 优先级：

- 可复现
- 决策可追踪
- 小步、可审查的改动
- 清晰的实验进展
- 稳定的分析、图表、表格和 TeX 手稿输出
- 只在流程真实变化时更新文档

Codex 是主要 agent 运行时。

Claude 兼容文件只作为链接层存在。
不要维护独立的 Claude 专用说明。

## 先读这些

- 项目概览：@README.md
- 实验看板：@DASHBOARD.md
- 项目初始化流程：@docs/agents/project-initialization.md
- Agent 文档索引：@docs/agents/README.md
- 仓库结构：@docs/agents/repo-map.md
- 数据流程：@docs/agents/data-project-workflow.md
- 实验流程：@docs/agents/experiment-workflow.md
- 写作和绘图风格：@docs/agents/writing-and-figure-style.md
- TeX 手稿流程：@docs/agents/tex-manuscript-workflow.md
- GitHub 论文协作流程：@docs/agents/paper-collaboration-workflow.md
- 源码组织：@src/README.md
- 脚本策略：@scripts/README.md

## 目录策略

- 不创建根目录 `agents/`。
- 不创建根目录 `dbschema/`。
- 不创建根目录 `reports/`。
- Agent 长文档放在 `docs/agents/`。
- 数据库 schema 文档放在 `docs/agents/dbschema/`。
- 项目研究计划放在 `docs/plans/`。
- 项目环境和操作偏好放在 `docs/project-preferences.md`。
- 只有真实可复用的 Codex skill 才放到 `.agents/skills/`，普通项目说明不要做成 skill。
- Codex custom agents 放在 `.codex/agents/`。
- 支持符号链接时，`CLAUDE.md` 指向本文件。
- `.claude/` 只保留兼容链接。

## 初始化策略

- 先配置 Python/TeX 环境。
- 再形成研究计划草案：@docs/plans/research-plan.md
- 同步记录环境和操作偏好：@docs/project-preferences.md
- 根据研究计划拆出第一个最小可运行实验。
- 不要在模板阶段替项目提前设计完整研究路线。

## 代码和脚本策略

- 可复用代码放在 `src/`，按真实项目功能模块组织。
- 源码组织规则见 @src/README.md。
- 集成脚本放在 `scripts/`。
- 脚本用于初始化环境，或按固定顺序调用一个或多个 `src/` 模块完成研究流程。
- 没有真实项目上下文前，不添加一次性 harness。

## 数据策略

- 原始数据放在 `data/raw/`。
- 中间数据放在 `data/interim/`。
- 清洗后数据放在 `data/processed/`。
- 外部来源数据放在 `data/external/`。
- 不覆盖原始数据。
- 不提交大型生成数据，除非项目明确需要。
- 非显然的数据转换必须记录。

## 实验策略

- 实验运行放在 `experiments/`。
- 每个实验至少记录配置、运行说明和结果位置。
- 通用图表输出到 `outputs/figures/`。
- 通用表格输出到 `outputs/tables/`。
- 手稿专用图表放到 `docs/writing/manuscript/figures/` 或 `docs/writing/manuscript/tables/`。
- 实验状态变化时更新 @DASHBOARD.md。

## 写作策略

- 默认写作输出使用 TeX。
- 手稿放在 `docs/writing/manuscript/`。
- 默认使用 CTAN `elsarticle` 的 Harvard author-year 样式。
- 默认只维护一个主 TeX 文档：`docs/writing/manuscript/main.tex`。
- 模板阶段不拆分章节文件。
- TeX 正文一行一句。
- 段落之间空一行。
- GitHub 上区分批注和修改：批注用 Issue 加正文 permalink，实际改写用小 PR 和 PR review。
- 不为没有正文改动的问题创建空 PR 或无意义 whitespace 改动。
- 图表必须能追踪到生成代码和数据。
- 写作和绘图指南见 @docs/agents/writing-and-figure-style.md。
- 论文协作规则见 @docs/agents/paper-collaboration-workflow.md。

## 文档策略

- Markdown 文档默认使用中文。
- 文件名使用 `kebab-case.md`。
- `docs/agents/` 保持浅层结构，除非项目增长出足够上下文。
- 优先维护少数被 `AGENTS.md` 引用的权威文档。
- 不写永久迁移说明，除非用户明确要求。
