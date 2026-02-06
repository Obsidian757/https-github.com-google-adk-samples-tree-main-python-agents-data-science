"""Tools for the Risk Scoring Agent."""

import logging
from datetime import date

from google.adk.tools import ToolContext

from ...db import execute_query

logger = logging.getLogger(__name__)

SEVERITY_SCORES = {"critical": 40, "high": 25, "medium": 10, "low": 3}
DATA_SENSITIVITY = {"classified": 20, "phi": 18, "pii": 12, "cui": 8, "public": 2}


async def calculate_risk_scores(
    tool_context: ToolContext,
) -> dict:
    """Calculate composite risk scores for all active AI systems.

    Scores are based on: gap severity, HIPAA relevance, deadline urgency,
    data sensitivity, and budget risk.

    Args:
        tool_context: ADK tool context.

    Returns:
        Dict with ranked risk scores and recommendations.
    """
    systems = execute_query("""
        SELECT s.system_id, s.system_name, s.vendor, s.agency,
               s.data_classification, s.hipaa_relevant
        FROM ai_systems s WHERE s.status = 'active'
    """)

    scored = []
    for sys in systems:
        sid = sys["system_id"]

        # Gap scores
        gaps = execute_query(f"""
            SELECT ga.severity, cf.compliance_deadline
            FROM gap_assessments ga
            JOIN compliance_frameworks cf ON ga.framework_id = cf.framework_id
            WHERE ga.system_id = '{sid}' AND ga.status != 'compliant'
        """)

        gap_score = sum(SEVERITY_SCORES.get(g["severity"], 0) for g in gaps)

        # HIPAA multiplier
        hipaa_mult = 2.0 if sys["hipaa_relevant"] else 1.0

        # Deadline urgency (nearest deadline)
        today = date.today()
        deadline_score = 0
        for g in gaps:
            dl = g.get("compliance_deadline")
            if dl:
                if isinstance(dl, str):
                    dl = date.fromisoformat(dl)
                days_left = (dl - today).days
                if days_left < 30:
                    deadline_score = max(deadline_score, 30)
                elif days_left < 60:
                    deadline_score = max(deadline_score, 20)
                elif days_left < 90:
                    deadline_score = max(deadline_score, 10)

        # Data sensitivity
        data_score = DATA_SENSITIVITY.get(sys["data_classification"], 2)

        # Budget risk
        usage = execute_query(f"""
            SELECT ut.credit_consumed, ut.credit_limit
            FROM usage_tracking ut
            JOIN licenses l ON ut.license_id = l.license_id
            WHERE l.system_id = '{sid}'
            ORDER BY ut.month DESC LIMIT 1
        """)
        budget_score = 0
        if usage and usage[0].get("credit_limit") and usage[0]["credit_limit"] > 0:
            ratio = usage[0]["credit_consumed"] / usage[0]["credit_limit"]
            if ratio > 0.9:
                budget_score = 15

        total = (gap_score * hipaa_mult) + deadline_score + data_score + budget_score

        scored.append({
            "system_id": sid,
            "system_name": sys["system_name"],
            "vendor": sys["vendor"],
            "agency": sys["agency"],
            "risk_score": round(total, 1),
            "gap_score": gap_score,
            "hipaa_multiplier": hipaa_mult,
            "deadline_urgency": deadline_score,
            "data_sensitivity": data_score,
            "budget_risk": budget_score,
            "open_gaps": len(gaps),
        })

    scored.sort(key=lambda x: x["risk_score"], reverse=True)
    tool_context.state["risk_scores"] = scored

    return {
        "status": "SUCCESS",
        "systems_scored": len(scored),
        "scores": scored,
    }
