"""Regulatory RAG Agent — federal AI compliance knowledge base."""

import os

from google.adk.agents import LlmAgent
from google.genai import types

from ...prompts import REGULATORY_RAG_INSTRUCTIONS

regulatory_rag_agent = LlmAgent(
    model=os.getenv("COMPLIANCE_AGENT_MODEL", "gemini-2.5-flash"),
    name="regulatory_rag_agent",
    instruction=REGULATORY_RAG_INSTRUCTIONS,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)
