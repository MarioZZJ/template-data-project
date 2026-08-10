# 研究源码

## 本目录职责

`src/` 存放直接参与数据获取、样本构造、统计分析、模型、图表和表格生成的研究源码。
它不是默认 Python package，源码按路径执行，不要求能够作为 Python 模块导入。

## 初始化时需要判断

- 研究是否是一条主要执行线，还是包含多个实质性研究模块。
- 每一步的输入、输出、依赖和执行顺序。
- Python、SQL 或 shell 哪种形式最直接、可审查。
- 哪些逻辑已经稳定到值得抽取复用，哪些仍应留在具体研究脚本中。

## 推荐建立的项目文件

单线研究优先使用平铺的三位编号脚本，例如：

- `001-data_import.py`
- `010-sample_construction.py`
- `020-descriptive_statistics.py`
- `030-main_analysis.py`
- `040-robustness_checks.py`
- `050-make_figures.py`
- `060-make_tables.py`
- `001-extract_bigquery.sql`
- `002-download_external_data.sh`

序号表达主执行顺序，并可留空号段供后续插入。
多个实质性研究模块可以按研究内容分目录；目录名表达研究模块，不使用 `utils`、`common`、`helpers`、`cleaning` 或 `analysis` 等泛化编程职责。

每个研究脚本开头记录 `Purpose`、`Inputs`、`Outputs` 和 `Run`。

## 当前项目配置

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

模板不创建虚假的编号脚本。
初始化时说明采用平铺编号还是实质性模块目录，并在根 README 登记计划执行顺序。

## 维护规则

- 根 `README.md` 的执行顺序表是完整命令和依赖关系的权威说明。
- 新增、删除或重排源码时同步更新执行顺序、`DASHBOARD.md` 和相关实验 README。
- 不为导入便利而增加包式占位文件。
- 不创建通用研究总控脚本。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/workflows/research-execution.md`
- `experiments/README.md`
