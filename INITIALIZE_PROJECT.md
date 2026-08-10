# 项目初始化清单

本文件只用于从模板生成后的首次项目初始化。
初始化完成后删除本文件，并形成一个只包含项目配置、不包含实质分析结果的提交。

## 1. 先读取项目契约

按顺序读取：

1. `AGENTS.md`
2. `README.md`
3. `DASHBOARD.md`
4. `docs/README.md`
5. `docs/plans/research-plan.md`
6. `docs/project-preferences.md`
7. `docs/data-sources.md`
8. `data/README.md`
9. `src/README.md`
10. `experiments/README.md`
11. `outputs/README.md`
12. `scripts/README.md`
13. `docs/writing/README.md`
14. `.agents/README.md`

Titanic 初始化提交的固定链接和差异说明见 `docs/examples/titanic-walkthrough.md`。
它只展示目录契约如何落到一个真实项目，不能机械复制其研究问题、变量、方法或数据获取方式。

## 2. 收集或确认研究上下文

至少确认：

- 研究问题、目标和不在范围内的事项；
- 研究对象、分析单位和时间范围；
- 数据来源、版本、访问限制和敏感性；
- 预期方法、比较对象、主要指标和证据标准；
- Python、SQL、TeX 和远程计算环境；
- BigQuery、MSSQL 或其他远程数据系统的实际标识；
- 正式图件、表格、数据摘要和手稿交付；
- Git 分支、论文批注、PR review 和发布方式。

无法确认但不阻塞初始化的内容明确写成“待确认”，不得补造。

## 3. 填写项目事实

填写以下文件：

- `README.md`：项目名称、研究问题、边界、正式交付和计划中的研究执行顺序；
- `DASHBOARD.md`：第一项依赖已满足、可以实际执行的任务；
- `docs/plans/research-plan.md`：研究设计草案、证据标准、风险和当前未知；
- `docs/project-preferences.md`：环境、资源、审批和协作偏好；
- `docs/data-sources.md`：所有已知本地或远程数据源及版本；
- 每个长期目录 README 的“当前项目配置”。

删除所有 `PROJECT-INIT` 注释，但保留目录 README 本身。

## 4. 决定源码和实验结构

- 单线研究优先在 `src/` 使用平铺的三位编号研究脚本。
- 有多个实质性研究模块时，可以按研究内容分目录。
- 不按 `ingest`、`cleaning`、`analysis`、`figures`、`utils` 等抽象编程职责提前创建空目录。
- 只在研究假设、方法比较、稳健性问题或阶段性研究问题已经明确时创建实验目录。
- 不创建空编号脚本；先在 README 执行顺序中登记计划，实际实现时再增加文件。

## 5. 配置环境和数据访问

- 检查 `.env.example`，只保留项目实际可能使用的配置区块；凭据只写入未跟踪的 `.env`、用户凭据目录或外部密钥系统。
- 根据真实分析需要编辑 `pyproject.toml`，再运行 `uv lock` 和 `uv sync`；不得手工编辑 `uv.lock`。
- 数据源涉及 BigQuery 时记录 project、location、dataset、table 和查询成本上限。
- 数据源涉及 MSSQL 时记录 host、database、schema、table 和证书校验要求，不记录密码。
- 数据源涉及 Kaggle 时确认许可或竞赛规则、认证方式和本地原始数据落点。

## 6. 保持模板边界

- 不建立 Notebook 目录或把交互式文档作为默认研究载体。
- 不引入 Snakemake、DVC、Kedro、Prefect、Airflow 等工作流引擎。
- 不建立 `run-all`、`make reproduce` 或同类总控 harness。
- 没有重复需求时，不创建新 skill、subagent、MCP 配置、provider 配置或 Agent 资产校验器。
- Agent 运行时配置和额外 harness 只由真实项目按需建立。

## 7. 完成初始化

1. 确认 `README.md` 的执行顺序足以指导下一项工作。
2. 确认 `DASHBOARD.md` 的第一项任务可以执行，或明确写出真实阻塞。
3. 运行 `rg -n "PROJECT-INIT|待初始化|TBD|YYYY-MM-DD"` 并逐项判断模板占位符是否应保留。
4. 运行 `git status --short`，确认没有数据或凭据进入暂存范围。
5. 删除 `INITIALIZE_PROJECT.md`。
6. 形成项目初始化提交；该提交不得包含实质分析结果。
