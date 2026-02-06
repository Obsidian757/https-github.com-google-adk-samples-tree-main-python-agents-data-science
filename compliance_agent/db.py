"""DuckDB database connection and query utilities for the compliance agent."""

import logging
import os

import duckdb

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("COMPLIANCE_DB_PATH", "compliance.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH, read_only=True)


def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return results as a list of dicts."""
    con = get_connection()
    try:
        result = con.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        logger.error("SQL execution error: %s", e)
        return [{"error": str(e)}]
    finally:
        con.close()


def get_schema_description() -> str:
    """Return a human-readable schema description for agent prompts."""
    con = duckdb.connect(DB_PATH, read_only=True)
    schema_parts = []
    try:
        tables = con.execute("SHOW TABLES").fetchall()
        for (table_name,) in tables:
            cols = con.execute(f"DESCRIBE {table_name}").fetchall()
            col_desc = ", ".join(f"{c[0]} ({c[1]})" for c in cols)
            row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            schema_parts.append(f"  {table_name} [{row_count} rows]: {col_desc}")
    finally:
        con.close()
    return "\n".join(schema_parts)
