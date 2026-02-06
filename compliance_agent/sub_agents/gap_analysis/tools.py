"""Tools for the Gap Analysis Agent."""

import logging

from google.adk.tools import ToolContext

from ...db import execute_query

logger = logging.getLogger(__name__)


async def query_gaps(
    sql_query: str,
    tool_context: ToolContext,
) -> dict:
    """Execute a SQL query to retrieve gap assessment data.

    Args:
        sql_query: SQL query against gap_assessments, ai_systems, and
            compliance_frameworks tables.
        tool_context: ADK tool context.

    Returns:
        Dict with query results.
    """
    results = execute_query(sql_query)
    if results and "error" in results[0]:
        return {"status": "ERROR", "error": results[0]["error"]}
    tool_context.state["gap_data"] = results
    return {"status": "SUCCESS", "rows": results, "row_count": len(results)}


async def generate_gap_report(
    system_id: str,
    tool_context: ToolContext,
) -> dict:
    """Generate a comprehensive gap report for a specific AI system.

    Args:
        system_id: The system_id to generate the report for (e.g., 'SYS-001').
        tool_context: ADK tool context.

    Returns:
        Dict with the full gap report including system info, gaps, and remediation plan.
    """
    system_info = execute_query(f"""
        SELECT s.*, l.total_seats, l.assigned_seats, l.active_seats,
               l.cost_per_seat, l.hipaa_tier
        FROM ai_systems s
        LEFT JOIN licenses l ON s.system_id = l.system_id
        WHERE s.system_id = '{system_id}'
    """)

    gaps = execute_query(f"""
        SELECT ga.*, cf.name as framework_name, cf.short_name,
               cf.compliance_deadline
        FROM gap_assessments ga
        JOIN compliance_frameworks cf ON ga.framework_id = cf.framework_id
        WHERE ga.system_id = '{system_id}'
        ORDER BY
            CASE ga.severity
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END
    """)

    total_effort = sum(g.get("estimated_effort_days", 0) for g in gaps)
    critical_count = sum(1 for g in gaps if g.get("severity") == "critical")
    high_count = sum(1 for g in gaps if g.get("severity") == "high")

    report = {
        "system": system_info[0] if system_info else {},
        "gaps": gaps,
        "summary": {
            "total_gaps": len(gaps),
            "critical": critical_count,
            "high": high_count,
            "total_effort_days": total_effort,
            "compliant_count": sum(1 for g in gaps if g.get("status") == "compliant"),
        },
    }

    tool_context.state["gap_report"] = report
    return report
