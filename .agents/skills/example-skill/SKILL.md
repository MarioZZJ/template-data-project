---
name: example-skill
description: 仅用于展示项目级 skill 的结构，只有用户明确要求检查或改造本示例时才使用。
---

# 项目级 Skill 格式示例

## 何时触发

仅当用户明确要求检查或改造本示例时触发，不自动参与初始化、数据、实验或写作任务。

## 先读取

读取 `AGENTS.md`、`README.md`、`DASHBOARD.md` 和 `.agents/README.md`。

## 执行步骤

1. 确认用户要求的示例改动范围。
2. 只修改本示例及必要的索引说明。
3. 不实现真实研究流程，不创建额外目录。

## 验证

检查 YAML front matter、链接和 `git diff --check`，确认没有把示例描述成默认工作流。
