# Agent 文档

这里放 agent 需要按需读取的项目流程文档。
`AGENTS.md` 是入口，本目录只补充更具体的项目规则。

## 权威位置

- 项目规则：@AGENTS.md
- 实验看板：@DASHBOARD.md
- 研究计划：@docs/plans/research-plan.md
- 项目偏好：@docs/project-preferences.md
- Codex skills：`.agents/skills/`
- Codex custom agents：`.codex/agents/`
- Claude 兼容层：`CLAUDE.md` 和 `.claude/` 符号链接

## 文档

- @docs/agents/project-initialization.md：项目初始化和上下文补齐流程。
- @docs/agents/repo-map.md：仓库结构。
- @docs/agents/data-project-workflow.md：数据分层和转换规则。
- @docs/agents/experiment-workflow.md：实验记录和推进规则。
- @docs/agents/writing-and-figure-style.md：科学写作和绘图风格。
- @docs/agents/tex-manuscript-workflow.md：Elsevier Harvard TeX 工作流。
- @docs/agents/dbschema/：数据库 schema 索引和表说明。

## 规则

- 不创建或使用根目录 `agents/`。
- 不重复 `AGENTS.md` 的内容。
- 普通项目说明不要做成 `.agents/skills/`。
- 项目上下文足够复杂时，再增加子目录。
- 进展状态变化时更新 @DASHBOARD.md。
