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

"""Financial Health Score Agent with Fi MCP integration"""

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from . import prompt

MODEL = "gemini-2.5-pro"

# Fi MCP toolset for financial data access
fi_mcp_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["mcp-remote", "https://fi-mcp-dev-56426154949.us-central1.run.app/mcp/stream"]
    )
)

financial_health_score_agent = Agent(
    model=MODEL,
    name="financial_health_score_agent", 
    instruction=prompt.FINANCIAL_HEALTH_SCORE_PROMPT,
    output_key="financial_health_score_output",
    tools=[fi_mcp_toolset],
) 