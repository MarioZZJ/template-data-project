# 实验

## 本目录职责

`experiments/` 记录围绕一个研究假设、方法比较、稳健性问题或阶段性研究问题形成的证据与决策。
它不为每次程序运行建立目录。

## 初始化时需要判断

- 哪个问题值得成为独立实验，而不是普通脚本运行。
- 实验依赖的数据版本、源码、参数和成功标准。
- 当前观察能支持什么决策，哪些仍是不确定性。
- 哪些结果应提升为正式图件或表格。

## 推荐建立的项目文件

推荐使用 `experiments/001-<slug>/README.md`，记录：

- 问题或假设；
- 数据及版本；
- 相关 `src/` 脚本；
- 参数和运行命令；
- 当前观察与不确定性；
- 决策；
- 正式输出链接。

实验目录不建立 `results/`。

## 当前项目配置

当前只有 `experiments/001-survival-associations/`，对应乘客特征与生存关联、年龄缺失敏感性和轻量模型验证。
普通重跑不新建实验目录。

## 维护规则

- 实验状态变化时同步更新 `DASHBOARD.md`。
- 正式结果只进入 `outputs/figures/` 和 `outputs/tables/`。
- 调试产物留在被忽略的临时位置，不进入正式输出。
- 结论变化时保留依据和决策时间，不覆盖原有证据语境。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/plans/research-plan.md`
- `docs/workflows/experiments.md`
