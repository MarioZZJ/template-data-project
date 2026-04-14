---
description: 占位示例 skill，演示 agents/skills/ 中的共享 skill 如何被 Claude Code 和 Codex 同时索引。可替换为真实内容。
---

这是一个占位 skill，无实际功能。

**共享 skill 机制说明：**
- skill 本体存放于 `agents/skills/<name>/SKILL.md`
- Claude Code 通过 `.claude/commands/TDP/<name>.md`（符号链接）访问，调用方式：`/TDP:<name>`
- Codex 通过 `.codex/skills/<name>.md`（符号链接）访问

将本文件内容替换为真实指令即可，符号链接无需改动。