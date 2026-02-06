"""12th House AI — Federal Compliance Governance Root Agent.

Orchestrates sub-agents for license querying, gap analysis,
risk scoring, and regulatory knowledge retrieval.
"""

import logging
import os
from datetime import date

from google.adk.agents import LlmAgent
from google.genai import types

from .db import get_schema_description
from .prompts import COMPLIANCE_ROOT_INSTRUCTIONS
from .tools import (
    call_license_query_agent,
    call_gap_analysis_agent,
    call_risk_scoring_agent,
    call_regulatory_rag_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_instructions() -> str:
    """Build root agent instructions with live schema."""
    try:
        schema = get_schema_description()
    except Exception:
        schema = "(Database not yet initialized — run seed_compliance_db.py first)"
    return COMPLIANCE_ROOT_INSTRUCTIONS.format(schema=schema)


root_agent = LlmAgent(
    model=os.getenv("COMPLIANCE_AGENT_MODEL", "gemini-2.5-flash"),
    name="compliance_root_agent",
    instruction=_build_instructions(),
    global_instruction=f"""
        You are the 12th House AI Compliance Governance Agent.
        A multi-agent system for federal AI compliance, license governance,
        and risk management. Built for SMB prime contractors.
        Today's date: {date.today()}
    """,
    tools=[
        call_license_query_agent,
        call_gap_analysis_agent,
        call_risk_scoring_agent,
        call_regulatory_rag_agent,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
