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
| 1 | `已验证` | `KAGGLE_STORAGE_TLS_HOST=storage.cloud.google.com bash src/001-download_titanic_data.sh` | Kaggle competition `titanic` | `data/raw/titanic/train.csv`、`test.csv` | 默认先用官方 CLI；当前网络对签名存储地址使用受信任 TLS 主机回退，不覆盖已有文件 |
| 2 | `已验证` | `uv run python src/010-prepare_analysis_data.py` | 两份官方原始 CSV | `data/processed/titanic-analysis.csv`、`data/interim/data-quality-summary.csv` | 核验 891×12 与 418×11，构造家庭和年龄缺失变量 |
| 3 | `已验证` | `uv run python src/020-descriptive_statistics.py` | 分析数据 | `data/interim/descriptive-statistics.csv`、`group-survival-rates.csv` | 按性别、舱位、年龄和家庭结构汇总 |
| 4 | `已验证` | `uv run python src/030-logistic_regression.py` | 分析数据 | 回归、模型拟合、模型规格和设计矩阵中间表 | 主模型使用中位数年龄与缺失指示，另做 714 人完整年龄敏感性 |
| 5 | `已验证` | `uv run python src/040-model_diagnostics.py` | 分析数据、主模型设计矩阵 | 性能、共线性、影响点和校准中间表 | 五折分层验证，随机种子 `20260810` |
| 6 | `已验证` | `uv run python src/050-make_figures.py` | 分组生存率、模型结果 | 两张 `outputs/figures/*.pdf` | 生成分组生存率图与主模型优势比图 |
| 7 | `已验证` | `uv run python src/060-make_tables.py` | 各步骤中间表 | `outputs/tables/` 中 17 个 CSV/TeX 文件 | 生成数据质量、描述、回归、敏感性、拟合、性能和诊断表 |

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

## 当前初步结果

- `train.csv` 有 891 名乘客，生存比例为 38.4%；年龄缺失 177 人。
- 观察生存率为女性 74.2%、男性 18.9%；一、二、三等舱分别为 63.0%、47.3%、24.2%。
- 调整其他模型变量后，女性相对男性的生存优势比为 14.89（95% CI 10.03--22.08）；一等舱相对三等舱为 5.54（2.72--11.29）。
- 年龄每增加 10 年的优势比为 0.68（0.58--0.79），家庭每增加 1 人为 0.74（0.63--0.86）。
- 五折分层交叉验证的样本外 ROC AUC 为 0.851，Brier score 为 0.144；这些指标只描述 `train.csv` 内部验证，不是 Kaggle 排名。
- 结果是观测数据中的条件关联，不支持因果解释；影响点和年龄缺失敏感性见正式诊断表。

## TeX 与 Elsevier

```bash
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

默认手稿使用 CTAN `elsarticle` 和 Harvard author-year 样式，正文保持一行一句。
当前轻量过程汇报直接引用中央正式图表，并明确它不是完整论文或最终研究结论。
构建和投稿目录是生成产物，不提交到 Git。

## 数据限制

官方 `test.csv` 没有 `Survived` 标签，只用于验证下载和结构兼容性。
主要关联分析与交叉验证只使用 `train.csv`，结论限于该观测数据中的统计关联。

## License

MIT
