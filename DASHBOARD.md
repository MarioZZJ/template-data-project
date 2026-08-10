# 项目看板

本文件是项目状态的唯一真源，只记录当前证据、下一步和正式输出，不保存长日志或重复研究计划。

状态使用：`TODO_READY`、`RUNNING`、`BLOCKED`、`DONE`、`DROPPED`。
任务开始、结束、失败、阻塞解除或正式输出变化时更新本表。

更新时间：2026-08-10

| ID | 状态 | 研究问题/任务 | 当前证据 | 下一步 | 相关脚本 | 正式输出 |
|---|---|---|---|---|---|---|
| `DATA-001` | `DONE` | 获取并核验官方 Titanic 数据 | `train.csv` 61,194 字节、SHA-256 `7d118f…010e9f6f`；`test.csv` 28,629 字节、`56023b…dd7dd52b2`；均被忽略且未跟踪 | 除非官方版本变化，不覆盖原始快照 | `src/001-download_titanic_data.sh` | `data/raw/titanic/README.md` |
| `PREP-010` | `DONE` | 构造分析数据并完成质量检查 | `train.csv` 891×12、`test.csv` 418×11；唯一键、重复、类型和取值检查无失败；训练集年龄缺失 177 | 数据版本变化时从原始快照重建 | `src/010-prepare_analysis_data.py` | `outputs/tables/data-quality-summary.csv` |
| `ANALYSIS-020` | `DONE` | 描述性统计、Logistic 回归、诊断和交叉验证 | 女性优势比 14.89（10.03--22.08），年龄每 10 年 0.68（0.58--0.79）；OOF AUC 0.851、Brier 0.144；VIF 均低于 3，54 个观测超过 Cook 阈值 | 在过程汇报中保留关联、缺失和影响点边界 | `src/020-` 至 `060-` | `outputs/figures/`、`outputs/tables/` |
| `REPORT-001` | `DONE` | 完成轻量 TeX 研究过程汇报 | 主文档直接引用中央 outputs；样式检查通过；PDF 共 7 页、289,002 字节，最终日志无未解析引用或版面溢出警告 | 新分析形成证据后再更新汇报 | `docs/writing/manuscript/main.tex` | `docs/writing/manuscript/build/main.pdf`（生成目录，不提交） |
