# 实验 001：乘客特征与生存关联

## 问题或假设

性别、舱位、年龄和家庭同行结构与 Titanic 乘客的生存概率存在可描述、可估计的条件关联。
本实验不把关联解释为因果效应。

## 数据及版本

- 主要数据：`data/raw/titanic/train.csv`，版本与 SHA-256 待首次下载后登记。
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

## 当前观察与未知

初始化阶段尚未获取数据或生成分析结果。
Kaggle 规则接受、认证状态、实际文件校验值、年龄缺失程度、模型稳定性和关联估计均待验证。

## 当前决策

- 状态：`BLOCKED`，blocked_by: `DATA-001`。
- 不进行 Kaggle submission。
- 正式输出只进入中央 `outputs/`。
