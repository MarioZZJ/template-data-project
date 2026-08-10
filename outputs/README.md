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

正式图件为 `survival-rates-by-characteristics.pdf` 和 `main-model-odds-ratios.pdf`，由 `src/050-make_figures.py` 生成。
正式表格包括数据质量、描述统计、分组生存率、回归、年龄缺失敏感性、模型拟合、性能、诊断和影响观测；除影响观测外均提供 CSV 与 TeX 版本，由 `src/060-make_tables.py` 生成。
所有名称使用稳定语义，不包含运行日期或 `final`、`latest` 后缀。

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
