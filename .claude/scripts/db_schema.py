"""
db-schema 命令脚本

用法：
    python .claude/scripts/db_schema.py                          # 列出 .env 中默认库的所有表并更新 INDEX.md
    python .claude/scripts/db_schema.py 库名.*                   # 列出指定库的所有表并更新 INDEX.md
    python .claude/scripts/db_schema.py 表名 [表名 ...]          # 查看当前库中指定表（默认 dbo schema）
    python .claude/scripts/db_schema.py 库名.schema名.表名 ...   # 查看指定库中的表并保存 schema 文件
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.mssql import get_columns, get_tables, get_row_count

SCHEMA_DIR = ROOT / "agents" / "dbschema"
INDEX_FILE = SCHEMA_DIR / "INDEX.md"


def parse_args(args: list[str]) -> list[dict]:
    if not args:
        return [{"database": None, "schema": None, "table": "*"}]
    results = []
    for arg in args:
        for part in arg.split(","):
            part = part.strip()
            if not part:
                continue
            segments = part.split(".")
            if len(segments) == 3:
                results.append({"database": segments[0], "schema": segments[1], "table": segments[2]})
            elif len(segments) == 2 and segments[1] == "*":
                results.append({"database": segments[0], "schema": None, "table": "*"})
            else:
                results.append({"database": None, "schema": "dbo", "table": part})
    return results


def format_data_type(row) -> str:
    dtype = row["DATA_TYPE"]
    max_len = row["CHARACTER_MAXIMUM_LENGTH"]
    if max_len is not None and max_len == max_len:
        max_len = int(max_len)
        return f"{dtype}(max)" if max_len == -1 else f"{dtype}({max_len})"
    return dtype


def read_existing_col_descriptions(filepath: Path) -> dict[str, str]:
    descriptions = {}
    if not filepath.exists():
        return descriptions
    for line in filepath.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\S+)\s*\|[^|]+\|\s*(.*?)\s*\|$", line)
        if m:
            col_name, desc = m.group(1), m.group(2)
            if col_name not in ("列名", "------", "---"):
                descriptions[col_name] = desc
    return descriptions


def read_existing_index_descriptions(database: str) -> dict[str, str]:
    """从 INDEX.md 中读取已有的表说明（{schema}.{table} -> 说明）"""
    descriptions = {}
    if not INDEX_FILE.exists():
        return descriptions
    in_db_section = False
    db_header = f"## {database}"
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip() == db_header:
            in_db_section = True
            continue
        if in_db_section:
            if line.startswith("## "):
                break
            m = re.match(r"^\|\s*(\S+\.\S+)\s*\|\s*(.*?)\s*\|$", line)
            if m:
                key, desc = m.group(1), m.group(2)
                if key not in ("表", "---", "------"):
                    descriptions[key] = desc
    return descriptions


def upsert_index_entry(database: str, schema: str, table: str):
    """在 INDEX.md 中添加或更新单个表条目，保留已有说明"""
    key = f"{schema}.{table}"
    existing_desc = read_existing_index_descriptions(database)
    desc = existing_desc.get(key, "")
    new_row = f"| {key} | {desc} |"
    db_header = f"## {database}"

    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text(encoding="utf-8")
    else:
        content = "# 数据库表索引\n\n供 agent 快速检索相关表，读取 `agents/dbschema/{库名}/{schema}.{表名}.md` 获取详细 schema。\n\n更新方式：运行 `/TDP:db-schema`。\n"

    if re.search(rf"^## {re.escape(database)}", content, re.MULTILINE):
        # 库 section 已存在
        if re.search(rf"^\| {re.escape(key)} \|", content, re.MULTILINE):
            # 条目已存在，无需改动（说明由用户维护）
            return
        # 追加到该库 section 的最后一个表格行之后
        lines = content.splitlines()
        in_section = False
        insert_after = -1
        for i, line in enumerate(lines):
            if line.strip() == db_header:
                in_section = True
                continue
            if in_section:
                if line.startswith("## "):
                    break
                if line.startswith("|"):
                    insert_after = i
        if insert_after >= 0:
            lines.insert(insert_after + 1, new_row)
        else:
            # section 存在但没有表格行，追加表头和新行
            for i, line in enumerate(lines):
                if line.strip() == db_header:
                    lines.insert(i + 1, new_row)
                    lines.insert(i + 1, "|----|------|")
                    lines.insert(i + 1, "| 表 | 说明 |")
                    lines.insert(i + 1, "")
                    break
        content = "\n".join(lines) + "\n"
    else:
        # 库 section 不存在，新建
        db_section = f"\n{db_header}\n\n| 表 | 说明 |\n|----|------|\n{new_row}\n"
        if not content.endswith("\n"):
            content += "\n"
        content += db_section

    INDEX_FILE.write_text(content, encoding="utf-8")


def update_index(database: str, tables_df):
    """将表列表更新到 INDEX.md，保留已填写的说明"""
    existing_desc = read_existing_index_descriptions(database)

    # 读取全文
    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text(encoding="utf-8")
    else:
        content = "# 数据库表索引\n\n供 agent 快速检索相关表，读取 `agents/dbschema/{库名}/{schema}.{表名}.md` 获取详细 schema。\n\n更新方式：运行 `/TDP:db-schema`。\n"

    # 构建该库的新 section
    new_rows = []
    for _, row in tables_df.iterrows():
        key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
        desc = existing_desc.get(key, "")
        new_rows.append(f"| {key} | {desc} |")

    db_section = f"## {database}\n\n| 表 | 说明 |\n|----|------|\n" + "\n".join(new_rows) + "\n"

    # 替换或追加
    pattern = rf"(## {re.escape(database)}\n[\s\S]*?)(?=^## |\Z)"
    if re.search(rf"^## {re.escape(database)}", content, re.MULTILINE):
        content = re.sub(pattern, db_section, content, flags=re.MULTILINE)
    else:
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + db_section

    INDEX_FILE.write_text(content, encoding="utf-8")


def list_tables(database: str = None):
    db = database or os.getenv("MSSQL_DATABASE")
    df = get_tables(db)
    print(f"\n数据库 [{db}] 共 {len(df)} 个表:\n")
    for _, row in df.iterrows():
        print(f"  {row['TABLE_SCHEMA']}.{row['TABLE_NAME']}")
    update_index(db, df)
    print(f"\n=> 已更新 agents/dbschema/INDEX.md")


def export_table(database: str, schema: str, table: str):
    cols = get_columns(table, schema=schema, database=database)
    if cols.empty:
        print(f"  [!] 表 {database}.{schema}.{table} 不存在或无列信息")
        return

    row_count = get_row_count(database, schema, table)

    out_dir = SCHEMA_DIR / database
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / f"{schema}.{table}.md"

    existing_desc = read_existing_col_descriptions(filepath)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {database}.{schema}.{table}",
        "",
        f"> 行数: {row_count:,}",
        f"> 更新时间: {now}",
        "",
        "| 列名 | 数据类型 | 说明 |",
        "|------|---------|------|",
    ]
    for _, row in cols.iterrows():
        col_name = row["COLUMN_NAME"]
        dtype = format_data_type(row)
        desc = existing_desc.get(col_name, "")
        lines.append(f"| {col_name} | {dtype} | {desc} |")

    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    upsert_index_entry(database, schema, table)

    print(f"\n## {database}.{schema}.{table}（{row_count:,} 行）\n")
    print(f"{'列名':<35} {'数据类型':<20} {'说明'}")
    print("-" * 70)
    for _, row in cols.iterrows():
        col_name = row["COLUMN_NAME"]
        dtype = format_data_type(row)
        desc = existing_desc.get(col_name, "")
        print(f"{col_name:<35} {dtype:<20} {desc}")
    print(f"\n=> 已保存到 agents/dbschema/{database}/{schema}.{table}.md")
    print(f"=> 已更新 agents/dbschema/INDEX.md")


def main():
    targets = parse_args(sys.argv[1:])
    for t in targets:
        if t["table"] == "*":
            list_tables(t["database"])
        else:
            db = t["database"] or os.getenv("MSSQL_DATABASE")
            schema = t["schema"] or "dbo"
            export_table(db, schema, t["table"])


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    main()
