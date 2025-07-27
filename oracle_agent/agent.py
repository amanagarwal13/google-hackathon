# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Financial Analysis and Prediction System - Main Coordinator"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from . import prompt
from .sub_agents.financial_analyzer.agent import financial_analyzer_agent
from .sub_agents.future_simulator.agent import future_simulator_agent
from .sub_agents.scenario_modeler.agent import scenario_modeler_agent
from .sub_agents.timeline_predictor.agent import timeline_predictor_agent
from .sub_agents.financial_health_score.agent import financial_health_score_agent

MODEL = "gemini-2.5-pro"

# Fi MCP toolset for the main analysis system
fi_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["mcp-remote", "https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream"]
    )
)

oracle_coordinator = LlmAgent(
    name="financial_analysis_coordinator",
    model=MODEL,
    description=(
        "Advanced financial analysis and prediction system that provides "
        "comprehensive data-driven insights, evidence-based forecasting, "
        "and quantitative assessment of financial scenarios and outcomes. "
        "Integrates multiple analytical sub-systems for complete financial evaluation."
    ),
    instruction=prompt.ORACLE_COORDINATOR_PROMPT,
    output_key="financial_analysis_output",
    tools=[
        fi_mcp_toolset,  # Direct access to Fi MCP for the coordinator
        AgentTool(agent=financial_analyzer_agent),
        AgentTool(agent=future_simulator_agent),
        AgentTool(agent=scenario_modeler_agent),
        AgentTool(agent=timeline_predictor_agent),
        AgentTool(agent=financial_health_score_agent),
    ],
)

root_agent = oracle_coordinator 