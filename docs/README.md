# 项目文档

这里保存研究设计、数据事实和稳定操作约定。任务状态、负责人、执行依赖与有效阶段授权由 Multica 维护；根 [DASHBOARD](../DASHBOARD.md) 只是生成快照。

## 研究事实

- [研究计划](plans/research-plan.md)：科学问题、全部阶段目标、当前阶段任务粒度、证据与呈现标准。
- [项目偏好](project-preferences.md)：环境、资源默认值、恢复和 Git 协作边界。
- [数据来源](data-sources.md)：版本、许可、访问限制、校验信息及固定输入映射。
- [实验说明](../experiments/README.md)：预设比较、观察、解释边界、决策和下游影响。

## 执行与写作

- [数据生命周期](workflows/data-lifecycle.md)：外部资产、固定输入、运行产物和数据源配置。
- [研究执行](workflows/research-execution.md)：五个运行入口、持久作业、交付与接续。
- [手稿工作流](workflows/manuscript.md)：手稿结构、编译、差异 PDF 和投稿打包。
- [写作与图表](workflows/writing-and-figures.md)：科学表述、数据图和正式成果选择。
- [协作约定](workflows/collaboration.md)：Multica 任务、GitHub 正文批注和 PR 的分工。
- [Titanic 历史导读](examples/titanic-walkthrough.md)：旧人工流程的固定快照与新版对应关系。

运行接口见 [仓库工具](../scripts/README.md)；项目入口见 [AGENTS.md](../AGENTS.md)。

优先修改已有权威文档。只有新的长期知识无法在现有主题中表达时才增加文件，使用 `kebab-case.md` 和相对链接。科学设计重大修订保留决定、依据和受影响成果，不靠复制多份状态文档记录过程。
