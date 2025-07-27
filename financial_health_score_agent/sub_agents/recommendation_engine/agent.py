"""Recommendation Engine Sub-Agent for Financial Health Improvements"""

from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

recommendation_agent = Agent(
    model=MODEL,
    name="recommendation_engine_agent",
    instruction=prompt.RECOMMENDATION_ENGINE_PROMPT,
    output_key="recommendations_output",
) 