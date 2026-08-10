# 写作

## 本目录职责

`docs/writing/` 保存研究写作入口和默认 TeX 手稿。
写作必须以已登记数据、实验记录和中央正式输出为依据。

## 初始化时需要判断

- 当前交付是过程汇报、工作论文还是投稿稿件。
- 投稿目标、作者、机构、语言和参考文献样式。
- 哪些正式图表进入正文，以及它们回答的研究问题。
- 协作者使用 Issue、PR review、PDF artifact 或其他方式审阅。

## 推荐建立的项目文件

- 默认维护 `manuscript/main.tex` 和 `manuscript/references.bib`。
- 模板阶段不拆章节；正文显著增长且协作确有需要时再决定。
- 其他写作产物只在项目明确需要时增加。

## 当前项目配置

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

当前使用 CTAN `elsarticle`、Harvard author-year 和单一主 TeX 文档。
初始化时填写写作阶段、语言、作者和投稿目标。

## 维护规则

- TeX 正文一行一句，段落之间空一行。
- 不虚构参考文献、统计结果、许可或研究结论。
- 手稿直接引用 `outputs/` 中的正式图表，不在本目录保存副本。
- 写作状态变化时更新 `DASHBOARD.md`。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/workflows/writing-and-figures.md`
- `docs/workflows/manuscript.md`
