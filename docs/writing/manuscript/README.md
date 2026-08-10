# TeX 手稿

## 本目录职责

`docs/writing/manuscript/` 保存单一主 TeX 文档、参考文献和生成目录入口。
它不保存正式图件或表格副本。

## 初始化时需要判断

- 文档类型、题目、作者、机构、语言和期刊目标。
- 当前阶段能够诚实报告的证据与限制。
- 需要引用的中央图表和可核实参考文献。
- 本地与 GitHub 构建环境是否完整。

## 推荐建立的项目文件

- `main.tex`：默认唯一主文档。
- `references.bib`：只保存已核实文献。
- `build/`：编译生成目录，不提交。
- `submission/`：投稿 bundle 生成目录，不提交。

## 当前项目配置

当前已经生成一份 Titanic 研究过程汇报，使用 `elsarticle` 单一主文档。
手稿从 `../../../outputs/figures/` 和 `../../../outputs/tables/` 直接引用正式产物，包含研究问题、数据限制、方法、初步结果、诊断、局限和下一步，并明确文档不是完整论文或最终结论。

## 维护规则

- 正文一行一句，段落之间空一行。
- 图件从 `../../../outputs/figures/` 引用，表格从 `../../../outputs/tables/` 引用。
- 构建前运行 `make check-tex-style`，构建后确认 PDF 非空。
- 投稿打包只通过仓库工具生成，并人工检查文件清单与许可。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/writing/README.md`
- `docs/workflows/manuscript.md`
- `docs/workflows/collaboration.md`
