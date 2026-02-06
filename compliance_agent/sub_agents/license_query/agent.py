"""License Query Agent — NL2SQL for compliance database queries."""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from ...prompts import LICENSE_QUERY_INSTRUCTIONS
from .tools import compliance_nl2sql

license_query_agent = LlmAgent(
    model=os.getenv("COMPLIANCE_AGENT_MODEL", "gemini-2.5-flash"),
    name="license_query_agent",
    instruction=LICENSE_QUERY_INSTRUCTIONS,
    tools=[compliance_nl2sql],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
