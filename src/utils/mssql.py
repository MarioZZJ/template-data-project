"""SQL Server 数据库连接工具（pyodbc）"""

import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_connection(database=None):
    db = database or os.getenv("MSSQL_DATABASE")
    return pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={os.getenv("MSSQL_HOST", "localhost")},{os.getenv("MSSQL_PORT", "1433")};'
        f'DATABASE={db};'
        f'UID={os.getenv("MSSQL_UID")};'
        f'PWD={os.getenv("MSSQL_PWD")}'
    )


def query(sql, params=None, database=None):
    conn = get_connection(database)
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def get_tables(database=None):
    db = database or os.getenv("MSSQL_DATABASE")
    sql = f"""
    SELECT TABLE_SCHEMA, TABLE_NAME
    FROM [{db}].INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    return query(sql, database=database)


def get_columns(table_name, schema="dbo", database=None):
    db = database or os.getenv("MSSQL_DATABASE")
    sql = f"""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
    FROM [{db}].INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?
    ORDER BY ORDINAL_POSITION
    """
    return query(sql, params=(table_name, schema), database=database)


def get_row_count(database, schema, table):
    sql = f"""
    SELECT SUM(p.rows) AS cnt
    FROM [{database}].sys.tables t
    INNER JOIN [{database}].sys.schemas s ON t.schema_id = s.schema_id
    INNER JOIN [{database}].sys.partitions p ON t.object_id = p.object_id
    WHERE s.name = ? AND t.name = ? AND p.index_id IN (0, 1)
    """
    df = query(sql, params=(schema, table), database=database)
    cnt = df["cnt"].iloc[0]
    return int(cnt) if cnt is not None and cnt == cnt else 0
