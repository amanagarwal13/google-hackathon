from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"

insight_synthesizer_agent = Agent(
    model=MODEL,
    name="insight_synthesizer_agent", 
    instruction=prompt.INSIGHT_SYNTHESIZER_PROMPT,
    output_key="insight_synthesis_output",
)