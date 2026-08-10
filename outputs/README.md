# 正式输出

## 本目录职责

`outputs/figures/` 和 `outputs/tables/` 是正式图件和表格的唯一真源。
正式输出供研究解释、手稿引用、审阅和发布使用，并由 Git 跟踪。

## 初始化时需要判断

- 项目需要哪些正式图件、表格和可机器读取的配套格式。
- 每个输出对应的研究问题、生成脚本、输入和关键参数。
- 期刊、协作者或下游工具对格式、尺寸和可访问性的要求。
- 哪些产物只是调试输出，不应进入本目录。

## 推荐建立的项目文件

- `figures/<stable-semantic-name>.pdf` 或必要的高分辨率位图。
- `tables/<stable-semantic-name>.csv` 及手稿需要的 `.tex` 表。
- 按实际需要增加简短清单，但不复制实验日志。

## 当前项目配置

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

模板仅保留 `figures/` 和 `tables/` 空叶子目录。
初始化时填写预期正式输出和命名规则。

## 维护规则

- 禁止使用 `final`、`final2`、`new`、`latest` 等不稳定命名。
- 临时和调试产物不得混入正式目录。
- 每个正式输出必须可追溯到生成脚本、输入和关键参数。
- 实验和手稿目录不得保存第二份正式结果副本。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/workflows/research-execution.md`
- `docs/workflows/writing-and-figures.md`
