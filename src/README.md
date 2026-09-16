# 研究源码

`src/` 保存直接参与取数、样本构造、统计分析、模型、图表和表格生成的源码。保持按路径执行及 `package=false`，无需为了模板成为 Python 包。

单线研究优先使用留有号段的三位编号，例如 `010-sample_construction.py`、`030-main_analysis.py`、`040-robustness_checks.py`。多个实质研究模块可以按问题分目录；不要提前按抽象编程职责搭空骨架，已有重复逻辑再按需要提取。

编号服务导航，科学依赖由研究计划解释，实际就绪顺序由 Multica 管理。模板不创建虚假编号脚本，也不在根 README 维护逐项命令总表。

## 每个步骤

脚本开头说明 `Purpose`、`Inputs`、`Outputs` 和 `Run`；实际参数、命令和版本保存在运行记录。读取固定版本输入，中间数据写 `RUN_DIR/data`，候选图表写 `OUTPUT_ROOT`；只有明确选择后的图表才进入仓库 `outputs/`。

检查关键样本量、键、缺失、范围和文件完整性；失败应返回非零状态并保留可定位证据。随机性可复现，非显然转换可追溯。程序成功不能代替科学解释。

启动长作业前，把实际改动纳入明确的代码提交，再使用外部代码快照和稳定环境；不得依赖即将被清理的临时工作树。

参见 [研究执行](../docs/workflows/research-execution.md)、[数据生命周期](../docs/workflows/data-lifecycle.md)、[实验说明](../experiments/README.md)。
