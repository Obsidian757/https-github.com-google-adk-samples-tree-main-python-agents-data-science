"""Risk Scoring Agent — composite risk scoring for AI systems."""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from ...prompts import RISK_SCORING_INSTRUCTIONS
from .tools import calculate_risk_scores

risk_scoring_agent = LlmAgent(
    model=os.getenv("COMPLIANCE_AGENT_MODEL", "gemini-2.5-flash"),
    name="risk_scoring_agent",
    instruction=RISK_SCORING_INSTRUCTIONS,
    tools=[calculate_risk_scores],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
