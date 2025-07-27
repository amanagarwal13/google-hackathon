"""Trend Analyzer Sub-Agent for Financial Health Score progression"""

from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

trend_analyzer_agent = Agent(
    model=MODEL,
    name="trend_analyzer_agent",
    instruction=prompt.TREND_ANALYZER_PROMPT,
    output_key="trend_analysis_output",
) 