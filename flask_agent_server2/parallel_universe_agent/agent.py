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

"""Financial Parallel Universe Explorer - Simplified Implementation"""

from google.adk.agents import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .sub_agents.insight_synthesizer.agent import insight_synthesizer_agent

MODEL = "gemini-2.5-pro"

# The Sequential Agent now only uses the insight synthesizer:
# - Main agent handles data extraction and analysis
# - Insight Synthesizer generates final JSON with insights and recommendations

parallel_universe_pipeline = SequentialAgent(
    name="ParallelUniversePipeline",
    sub_agents=[
        insight_synthesizer_agent,    # Final JSON synthesis → insight_synthesis_output
    ],
    description=(
        "Simplified pipeline that transforms financial history into a comprehensive "
        "JSON multiverse analysis showing actual decisions vs alternative timelines "
        "and their financial impacts. Main agent handles most processing, with "
        "insight synthesizer generating the final output."
    ),
    # The insight synthesizer will receive all data from the main agent
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = parallel_universe_pipeline