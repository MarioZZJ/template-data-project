# 项目实验看板

Agent 接手项目进展先读这里。
这里只放研究计划、实验进展、结果位置和下一步，不放长日志、不放完整计划、不放实现细节。

详细研究想法先写到 @docs/plans/research-plan.md。
环境和操作偏好写到 @docs/project-preferences.md。
具体实验配置和记录按需放到 `experiments/<id>/`。

## 更新规则

- 状态只用：`TODO_READY` / `RUNNING` / `BLOCKED` / `DONE` / `DROPPED`
- 每个研究阶段或实验一行。
- 路径必须能直接定位到文件或目录。
- `TODO_READY` 表示依赖已满足，现在可推进。
- `BLOCKED` 表示当前不能推进；原因写在 `进展/结论`。
- 等依赖用 `blocked_by: <ID>` 明确引用阻塞项。
- 开始、结束、失败、移动结果时更新本文件。
- 不贴日志全文；日志只写路径。
- 不急着把所有实验计划写满，先让研究计划文档收敛问题、数据、方法和偏好。

## 状态语义

- `DONE`：结果可复用，除非发现数据或口径错误，不要重跑。
- `RUNNING`：先查进度和日志，不要重启或覆盖。
- `TODO_READY`：依赖已满足，是当前可推进项。
- `BLOCKED`：有明确依赖、缺文件、工具缺口、权限问题或人工决策。
- `DROPPED`：保留归档，不再推进。

## 当前看板

更新时间：YYYY-MM-DD

| ID | 状态 | 依赖ID | 工作项 | 配置/计划 | 进展/结论 | 结果位置 | 下一步 |
|---|---|---|---|---|---|---|---|
| `PLAN-INIT` | `TODO_READY` | 无 | 形成研究计划草案 | @docs/plans/research-plan.md | 写清研究问题、数据来源、初始方法、环境偏好和第一步实验，不要求一次性写完所有细节 | `docs/plans/` | 完成后拆出首个可运行实验 |
| `EXP-001-BASELINE` | `BLOCKED` | `PLAN-INIT` | 第一个基线实验 | @docs/plans/research-plan.md | blocked_by: `PLAN-INIT`；研究问题和首个实验口径尚未确认 | `experiments/` | 根据研究计划创建最小实验配置和运行记录 |
