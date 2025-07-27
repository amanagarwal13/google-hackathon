# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Financial Health Score Agent - Comprehensive Financial Wellness Assessment"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .tools import (
    calculate_financial_health_score,
    generate_weekly_trend_chart,
    generate_factor_breakdown_chart,
    generate_improvement_projection_chart,
    generate_score_distribution_chart
)
from .sub_agents.trend_analyzer import trend_analyzer_agent
from .sub_agents.recommendation_engine import recommendation_agent

MODEL = "gemini-2.5-pro"

# Fi MCP toolset for comprehensive financial data
fi_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["mcp-remote", "https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream"]
    )
)

financial_health_agent = LlmAgent(
    name="financial_health_scorer",
    model=MODEL,
    description=(
        "Comprehensive financial health assessment agent that calculates a "
        "single financial wellness score (0-1000) based on multiple factors "
        "including liquidity, savings rate, spending patterns, and investment "
        "diversification. Provides actionable insights, trend analysis, and "
        "visual charts showing score progression and factor breakdowns."
    ),
    instruction=prompt.FINANCIAL_HEALTH_PROMPT,
    output_key="financial_health_output",
    tools=[
        fi_mcp_toolset,
        calculate_financial_health_score,
        generate_weekly_trend_chart,
        generate_factor_breakdown_chart,
        generate_improvement_projection_chart,
        generate_score_distribution_chart,
        AgentTool(agent=trend_analyzer_agent),
        AgentTool(agent=recommendation_agent),
    ],
)

root_agent = financial_health_agent 