# 项目看板

本文件是项目状态的唯一真源，只记录当前证据、下一步和正式输出，不保存长日志或重复研究计划。

状态使用：`TODO_READY`、`RUNNING`、`BLOCKED`、`DONE`、`DROPPED`。
任务开始、结束、失败、阻塞解除或正式输出变化时更新本表。

更新时间：2026-08-10

| ID | 状态 | 研究问题/任务 | 当前证据 | 下一步 | 相关脚本 | 正式输出 |
|---|---|---|---|---|---|---|
| `DATA-001` | `TODO_READY` | 获取并核验官方 Titanic 数据 | 竞赛 slug、预期文件和安全获取方式已登记；规则接受与认证尚待命令验证 | 执行数据获取脚本并记录大小与 SHA-256 | `src/001-download_titanic_data.sh`（待建立） | — |
| `PREP-010` | `BLOCKED` | 构造分析数据并完成质量检查 | blocked_by: `DATA-001` | 数据到位后构造家庭同行变量并核验样本 | `src/010-prepare_analysis_data.py`（待建立） | — |
| `ANALYSIS-020` | `BLOCKED` | 描述性统计、Logistic 回归、诊断和交叉验证 | blocked_by: `PREP-010` | 分析数据完成后按 README 顺序运行 | `src/020-` 至 `060-`（待建立） | 计划见 `outputs/README.md` |
| `REPORT-001` | `BLOCKED` | 完成轻量 TeX 研究过程汇报 | blocked_by: `ANALYSIS-020` | 正式图表完成后更新并编译主 TeX 文档 | `docs/writing/manuscript/main.tex` | `docs/writing/manuscript/build/main.pdf`（生成目录） |
