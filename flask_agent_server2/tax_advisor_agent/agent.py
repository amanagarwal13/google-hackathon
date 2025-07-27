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

"""Tax Advisor Agent - AI-powered Tax Planning and Optimization System"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from . import prompt

# Direct imports from sub-agent modules
from .sub_agents.tax_analyzer.agent import tax_analyzer_agent
from .sub_agents.deduction_optimizer.agent import deduction_optimizer_agent
from .sub_agents.tax_planner.agent import tax_planner_agent
from .sub_agents.tax_scenario_modeler.agent import tax_scenario_modeler_agent

MODEL = "gemini-2.5-pro"

# Fi MCP toolset for accessing financial data for tax calculations
fi_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["mcp-remote", "https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream"]
    )
)

tax_advisor_coordinator = LlmAgent(
    name="tax_advisor_coordinator",
    model=MODEL,
    description=(
        "Professional AI-powered Tax Advisor that provides comprehensive tax planning "
        "and optimization strategies based on rigorous analysis of financial data. "
        "Delivers calculated, evidence-based recommendations for tax regime selection, "
        "deduction optimization, and strategic tax planning with transparent methodology."
    ),
    instruction=prompt.TAX_ADVISOR_COORDINATOR_PROMPT,
    output_key="tax_advisor_coordinator_output",
    tools=[
        fi_mcp_toolset,  # Direct access to Fi MCP for financial data
        AgentTool(agent=tax_analyzer_agent),
        AgentTool(agent=deduction_optimizer_agent),
        AgentTool(agent=tax_planner_agent),
        AgentTool(agent=tax_scenario_modeler_agent),
    ],
)

root_agent = tax_advisor_coordinator 