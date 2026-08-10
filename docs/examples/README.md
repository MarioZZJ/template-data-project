# 项目示例

## 本目录职责

`docs/examples/` 解释模板如何在外部分支或固定历史中演化成真实研究项目。
示例用于比较结构和决策，不是可直接复制的研究方案。

## 初始化时需要判断

- 哪个示例阶段与当前初始化、分析或写作问题对应。
- 示例中的研究问题、变量、方法、数据许可和环境是否适用于当前项目。
- 应借鉴目录契约还是仅阅读某个固定提交差异。

## 推荐建立的项目文件

- `titanic-walkthrough.md`：模板附带的三阶段固定历史说明。
- 只有新示例具有独立教学价值且能用固定提交审计时才增加文件。

## 当前项目配置

当前分支本身实现 Titanic 三阶段示例，不新增其他示例。
最终固定 SHA 和阶段差异仍由默认分支的 `titanic-walkthrough.md` 维护。

## 维护规则

- 示例链接使用固定 SHA，不只引用浮动分支 HEAD。
- 不建议 merge 或 cherry-pick 整个示例。
- 示例事实变化时更新比较链接和重点文件，不把示例内容写入模板占位区。
- 新项目只逐项适配适用结构。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/workflows/research-execution.md`
- `docs/workflows/manuscript.md`
