# 数据库表结构查看与导出

查看 SQL Server 数据库的表结构，保存为 schema 文件，并更新 `agents/dbschema/INDEX.md` 索引。

## 使用方式

`$ARGUMENTS` 可以是：
- 空：列出 `.env` 中 `MSSQL_DATABASE` 的所有表，并更新 INDEX.md
- `库名.*`：列出指定库的所有表，并更新 INDEX.md
- `表名`（多个用空格或逗号分隔）：查看当前库中指定表（默认 dbo schema）
- `库名.schema名.表名`：查看指定库中的表

## 执行

```bash
source .venv/bin/activate && python .claude/scripts/db_schema.py $ARGUMENTS
```

将命令输出展示给用户，并提示用户可以在生成的 schema 文件的"说明"列手动补充字段含义。

## 输出位置

- schema 文件：`agents/dbschema/{库名}/{schema名}.{表名}.md`
- 表索引：`agents/dbschema/INDEX.md`（供 agent 快速检索相关表）
- 已有文件会被覆盖，但保留用户已填写的"说明"列内容
