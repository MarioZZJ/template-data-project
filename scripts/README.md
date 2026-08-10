# 仓库工具

## 本目录职责

`scripts/` 只存放跨研究内容的仓库工具，例如 TeX 环境检查、TeX 风格检查、手稿 diff 和 Elsevier 投稿打包。
具体数据获取、分析、图表和表格步骤属于 `src/`。

## 初始化时需要判断

- 现有 TeX 和投稿工具是否符合项目的期刊与协作方式。
- 项目是否出现了真实、重复且跨研究内容的仓库维护需求。
- 新工具是否会与根 README 的人工执行顺序或 `src/` 职责重叠。

## 推荐建立的项目文件

模板已有：

- `init-tex-env.sh`
- `check-tex-sentence-lines.py`
- `build-manuscript-diff.sh`
- `prepare-elsevier-submission.sh`

不要增加 `run-all`、研究流水线、通用数据库连接器、通用下载器、自动实验编排器或 Agent 资产校验器。

## 当前项目配置

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

当前使用模板提供的 TeX 与 Elsevier 工具。
初始化时说明是否调整投稿目标或协作方式。

## 维护规则

- 修改脚本前先读本文件和相应工作流文档。
- shell 脚本至少通过 `bash -n`；修改后运行其直接调用路径。
- 只在流程真实变化时更新文档，不保留重复环境入口。
- 生成目录和临时文件不提交。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/workflows/manuscript.md`
- `docs/workflows/collaboration.md`
