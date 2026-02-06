"""Root-level tools for the Compliance Governance Agent.

These wrap sub-agents as callable tools for the root orchestrator.
"""

import logging

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import (
    license_query_agent,
    gap_analysis_agent,
    risk_scoring_agent,
    regulatory_rag_agent,
)

logger = logging.getLogger(__name__)


async def call_license_query_agent(
    question: str,
    tool_context: ToolContext,
):
    """Query the compliance database for license, usage, and cost information.

    Use this tool when the user asks about:
    - License counts, seat allocation, or unused seats
    - Credit consumption or cost analysis
    - Usage trends or active user counts
    - O365 restrictions or HIPAA tier configurations
    - Any question that needs SQL against the compliance database

    Args:
        question: Natural language question about licenses or usage.
        tool_context: ADK tool context.

    Returns:
        Query results from the compliance database.
    """
    logger.info("call_license_query_agent: %s", question)
    agent_tool = AgentTool(agent=license_query_agent)
    output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["license_query_output"] = output
    return output


async def call_gap_analysis_agent(
    question: str,
    tool_context: ToolContext,
):
    """Analyze compliance gaps across AI systems and regulatory frameworks.

    Use this tool when the user asks about:
    - Compliance status or gap assessments
    - What requirements are missing for a specific system
    - Remediation plans or effort estimates
    - Compliance visualizations or gap reports

    Args:
        question: Natural language question about compliance gaps.
        tool_context: ADK tool context.

    Returns:
        Gap analysis results with remediation recommendations.
    """
    logger.info("call_gap_analysis_agent: %s", question)
    agent_tool = AgentTool(agent=gap_analysis_agent)
    output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["gap_analysis_output"] = output
    return output


async def call_risk_scoring_agent(
    question: str,
    tool_context: ToolContext,
):
    """Calculate and rank AI systems by compliance risk score.

    Use this tool when the user asks about:
    - Which systems are highest risk
    - Risk prioritization or ranking
    - What to fix first
    - Overall compliance posture

    Args:
        question: Natural language question about risk or priorities.
        tool_context: ADK tool context.

    Returns:
        Ranked risk scores with recommendations.
    """
    logger.info("call_risk_scoring_agent: %s", question)
    agent_tool = AgentTool(agent=risk_scoring_agent)
    output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["risk_scoring_output"] = output
    return output


async def call_regulatory_rag_agent(
    question: str,
    tool_context: ToolContext,
):
    """Answer questions about federal AI compliance regulations and frameworks.

    Use this tool when the user asks about:
    - Specific OMB memos (M-25-21, M-25-22)
    - NIST AI Risk Management Framework
    - Executive Order 14110
    - HIPAA requirements for AI systems
    - DFARS or agency-specific requirements
    - What a regulation requires or means

    Args:
        question: Natural language question about regulations.
        tool_context: ADK tool context.

    Returns:
        Regulatory explanation with citations and requirements.
    """
    logger.info("call_regulatory_rag_agent: %s", question)
    agent_tool = AgentTool(agent=regulatory_rag_agent)
    output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["regulatory_rag_output"] = output
    return output
