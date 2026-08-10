# 项目级 Skills

## 本目录职责

`.agents/skills/` 只存放已经在真实项目中出现、值得重复调用且边界稳定的项目级工作流。
通用项目规则应写入 `AGENTS.md`、目录 README 或 `docs/`，不能为了“Agent 友好”全部转成 skill。

## 初始化时需要判断

- 项目是否已经出现重复、稳定且可以明确验证的工作流。
- 该流程是否确实需要按需加载的专门说明，而不是一段普通文档。
- 触发条件、输入、输出和失败边界是否足够清楚。

## 推荐建立的项目文件

- 只有实际重复需求出现后，才考虑建立 `.agents/skills/<skill-name>/SKILL.md`。
- 模板只提供 `example-skill/` 作为格式示例，不预设初始化、数据获取、实验或写作技能。

## 当前项目配置

Titanic 项目没有出现需要沉淀为项目 skill 的重复工作流。
保留不自动参与项目工作的 `example-skill/` 作为模板格式示例，不新增项目专属 skill。

## 维护规则

- 新增 skill 前先确认真实重复需求和验证方式。
- 普通说明移回相应目录 README 或 `docs/`。
- 删除已失去稳定触发条件或不再复用的 skill。
- 不在本目录建立 subagent、provider、model、sandbox 或 MCP 配置。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/README.md`
