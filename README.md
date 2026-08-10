# Titanic 生存关联分析

本项目用 Titanic 官方竞赛数据展示模板如何演化为一项可复现的定量研究。
重点是乘客特征与生存概率的关联、研究过程记录和轻量 TeX 汇报，不是 Kaggle 排名教程。

## 当前项目

- 项目名称：Titanic 生存关联分析。
- 研究问题：乘客的性别、舱位、年龄和家庭同行结构，与其生存概率之间存在怎样的关联？
- 研究对象与分析单位：`train.csv` 中每位有生存标签的 Titanic 乘客；分析单位为乘客。
- 项目边界：开展描述性统计、Logistic 回归、年龄缺失敏感性、简单诊断和分层交叉验证；不作因果解释，不使用 `test.csv` 评价模型，不向 Kaggle 提交预测。
- 正式交付：中央正式图件、正式表格、可重建分析数据和一份轻量 TeX 研究过程汇报。

## 环境

本项目使用 Python 3.12、`uv` 和外部 Kaggle CLI。
先同步锁定依赖：

```bash
make init-python
```

TeX 环境可独立检查：

```bash
make init-tex
```

## 研究执行顺序

本表是完整运行命令、输入、输出和依赖关系的权威说明。
源码编号提供视觉顺序，但不能替代本表；新增、删除或重排步骤时，同步更新本表、`DASHBOARD.md` 和相关实验 README。

| 顺序 | 状态 | 命令 | 输入 | 输出 | 说明 |
|---:|---|---|---|---|---|
| 1 | `计划` | `bash src/001-download_titanic_data.sh` | Kaggle competition `titanic` | `data/raw/titanic/train.csv`、`test.csv` | 先接受规则并完成认证；不覆盖已有原始文件 |
| 2 | `计划` | `uv run python src/010-prepare_analysis_data.py` | `data/raw/titanic/train.csv`、`test.csv` | `data/processed/titanic-analysis.csv`、数据质量中间表 | 构造 `FamilySize`、`TravelAlone` 和年龄缺失标记 |
| 3 | `计划` | `uv run python src/020-descriptive_statistics.py` | 分析数据 | 描述统计与分组生存率中间表 | 按性别、舱位、年龄和家庭结构汇总 |
| 4 | `计划` | `uv run python src/030-logistic_regression.py` | 分析数据 | Logistic 回归与年龄缺失敏感性中间表 | 报告优势比、置信区间和必要统计量 |
| 5 | `计划` | `uv run python src/040-model_diagnostics.py` | 分析数据 | 诊断与分层交叉验证中间表 | 固定随机种子，报告 ROC AUC 与 Brier score |
| 6 | `计划` | `uv run python src/050-make_figures.py` | 分组生存率、模型结果 | `outputs/figures/` 正式图件 | 生成分组生存率图与优势比图 |
| 7 | `计划` | `uv run python src/060-make_tables.py` | 各步骤中间表 | `outputs/tables/` 正式表格 | 输出稳定语义名称的 CSV 和 TeX 表 |

不提供一键运行全部研究的入口。
研究者按表中顺序逐项运行和核验。

## 目录结构

- `data/`：原始、中间、分析就绪和外部数据分层。
- `src/`：直接参与研究过程的编号源码或实质性研究模块。
- `experiments/`：围绕研究假设、方法比较或稳健性问题的记录。
- `outputs/figures/`、`outputs/tables/`：正式图件和表格的唯一真源。
- `scripts/`：跨研究内容的仓库工具，主要服务 TeX 和投稿。
- `docs/`：研究计划、长期事实、工作流、示例和手稿。
- `.agents/`：真实项目按需沉淀的少量稳定 skill；模板只含格式示例。

本项目采用平铺编号源码；完整结构见 `docs/repository-structure.md`。

## 状态与正式输出

`DASHBOARD.md` 是项目状态的唯一真源。
正式图件和表格只保存在 `outputs/`，实验目录和手稿目录不维护第二份副本。

## TeX 与 Elsevier

```bash
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

默认手稿使用 CTAN `elsarticle` 和 Harvard author-year 样式，正文保持一行一句。
构建和投稿目录是生成产物，不提交到 Git。

## 数据限制

官方 `test.csv` 没有 `Survived` 标签，只用于验证下载和结构兼容性。
主要关联分析与交叉验证只使用 `train.csv`，结论限于该观测数据中的统计关联。

## License

MIT
