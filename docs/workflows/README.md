# 项目工作流

## 本目录职责

`docs/workflows/` 维护跨项目阶段仍然稳定的数据、研究执行、实验、写作、手稿和协作规则。
它描述如何工作，不保存当前任务状态或重复具体项目事实。

## 初始化时需要判断

- 哪些模板规则适用于本项目，哪些需要按真实环境调整。
- 数据系统、分析方法、投稿目标和协作方式是否引入额外稳定约束。
- 哪些操作需要人工审批或外部系统权限。

## 推荐建立的项目文件

- `data-lifecycle.md`
- `research-execution.md`
- `experiments.md`
- `writing-and-figures.md`
- `manuscript.md`
- `collaboration.md`

只有出现新的稳定工作流时才增加文件。

## 当前项目配置

当前采用模板提供的六项工作流。
数据生命周期只使用 Kaggle CSV 路径，不使用 BigQuery 或 MSSQL；研究执行采用根 README 的七个计划步骤；TeX 目标是轻量研究过程汇报。

## 维护规则

- 流程真实变化时更新本目录和相应目录 README。
- 当前状态写入 `DASHBOARD.md`，实际执行命令写入根 README。
- 不为一次性迁移、单次运行或运行时配置增加长期工作流。
- 链接到权威事实，不复制大段内容。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/README.md`
