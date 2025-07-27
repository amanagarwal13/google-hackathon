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

"""Deduction Optimizer Agent - Maximizing Tax Deductions and Exemptions"""

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from . import prompt

MODEL = "gemini-2.5-pro"

# Fi MCP toolset for financial data access
fi_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["mcp-remote", "https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream"]
    )
)

# Wrap google_search in AgentTool for compatibility
search_agent = Agent(
    model="gemini-2.5-flash",
    name="deduction_search_agent",
    instruction="You're a specialist in tax deduction and exemption related Google Search.",
    tools=[google_search],
)
search_tool = AgentTool(search_agent)

deduction_optimizer_agent = Agent(
    model=MODEL,
    name="deduction_optimizer_agent",
    description=(
        "Tax deduction optimization specialist that identifies and maximizes "
        "all possible tax deductions, exemptions, and tax-saving opportunities "
        "from available financial data and investment patterns with access to "
        "current tax regulations and deduction rules."
    ),
    instruction=prompt.DEDUCTION_OPTIMIZER_PROMPT,
    output_key="deduction_optimizer_output",
    tools=[fi_mcp_toolset, search_tool],  # Now both are compatible tool types
) 