# 实验 001：乘客特征与生存关联

## 问题或假设

性别、舱位、年龄和家庭同行结构与 Titanic 乘客的生存概率存在可描述、可估计的条件关联。
本实验不把关联解释为因果效应。

## 数据及版本

- 主要数据：`data/raw/titanic/train.csv`，61,194 字节，SHA-256 `7d118f…010e9f6f`。
- 结构兼容性：`data/raw/titanic/test.csv`，不含标签，不用于主要分析或交叉验证。
- 分析数据：计划生成 `data/processed/titanic-analysis.csv`，可重建且不提交。

## 变量

- 结果：`Survived`。
- 主要解释变量：`Sex`、`Pclass`、`Age`、`FamilySize`、`TravelAlone`。
- 可解释调整变量：`Fare`、`Embarked`。
- `FamilySize = SibSp + Parch + 1`；`TravelAlone` 表示 `FamilySize == 1`。

## 计划分析

1. 核验数据结构、唯一键、类型、缺失、重复和合理范围。
2. 计算总体及按主要变量分组的描述统计和生存率。
3. 拟合主 Logistic 回归，报告优势比与 95% 置信区间。
4. 主分析对年龄做训练折内中位数填补并保留缺失指示，另做完整案例敏感性。
5. 检查共线性或影响点，以及校准或拟合情况。
6. 使用固定种子的分层交叉验证报告 ROC AUC 与 Brier score。

## 预期正式输出

- `outputs/figures/survival-rates-by-characteristics.pdf`
- `outputs/figures/main-model-odds-ratios.pdf`
- `outputs/tables/descriptive-statistics.csv` 与 `.tex`
- `outputs/tables/logistic-regression-results.csv` 与 `.tex`
- `outputs/tables/model-performance.csv` 与 `.tex`
- 诊断和年龄缺失敏感性表按分析需要增加稳定语义名称。

## 当前观察

- 样本为 891 人，342 人生存；年龄缺失 177 人，其他数据质量检查无失败。
- 女性与男性观察生存率分别为 74.2% 和 18.9%；一、二、三等舱分别为 63.0%、47.3% 和 24.2%。
- 主模型中，女性相对男性优势比为 14.89（95% CI 10.03--22.08），一等舱相对三等舱为 5.54（2.72--11.29）。
- 年龄每增加 10 年优势比为 0.68（0.58--0.79），家庭每增加 1 人为 0.74（0.63--0.86）。
- 完整年龄样本方向总体一致，但一等舱估计由 5.54 变为 9.07，且部分次要调整变量区间较宽，不能把敏感性结果描述为完全不变。
- 五折样本外 ROC AUC 为 0.851，Brier score 为 0.144；校准截距 -0.013、斜率 0.996。
- VIF 均低于 3；54 人超过 Cook 距离 `4/n` 阈值，提示结果解释需保留影响点边界。

## 当前决策

- 状态：`DONE`；分析步骤和正式输出已从官方原始快照重建。
- 不进行 Kaggle submission。
- 正式输出只进入中央 `outputs/`。
- 以上是条件关联和轻量内部验证，不构成因果估计或竞赛排名。
