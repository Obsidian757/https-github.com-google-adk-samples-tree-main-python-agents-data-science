"""Gap Analysis Agent — compliance gap assessment and visualization."""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from ...prompts import GAP_ANALYSIS_INSTRUCTIONS
from .tools import query_gaps, generate_gap_report

gap_analysis_agent = LlmAgent(
    model=os.getenv("COMPLIANCE_AGENT_MODEL", "gemini-2.5-flash"),
    name="gap_analysis_agent",
    instruction=GAP_ANALYSIS_INSTRUCTIONS,
    tools=[query_gaps, generate_gap_report],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)
