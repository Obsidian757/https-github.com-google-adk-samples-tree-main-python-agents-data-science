"""Tools for the License Query Agent — executes SQL against compliance DuckDB."""

import logging

from google.adk.tools import ToolContext

from ...db import execute_query

logger = logging.getLogger(__name__)


async def compliance_nl2sql(
    sql_query: str,
    tool_context: ToolContext,
) -> dict:
    """Execute a SQL query against the compliance DuckDB database.

    Args:
        sql_query: A valid DuckDB SQL query to execute against the compliance
            database tables (ai_systems, licenses, usage_tracking,
            compliance_frameworks, gap_assessments).
        tool_context: ADK tool context for state management.

    Returns:
        Dict with 'status' and 'rows' (or 'error').
    """
    logger.info("Executing compliance SQL: %s", sql_query)

    results = execute_query(sql_query)

    if results and "error" in results[0]:
        return {"status": "ERROR", "error": results[0]["error"]}

    tool_context.state["last_query_result"] = results
    return {"status": "SUCCESS", "rows": results, "row_count": len(results)}
