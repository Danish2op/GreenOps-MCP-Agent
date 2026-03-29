"""GreenOps Carbon-Aware Compute Routing Agent — Google ADK.

Connects to the GreenOps FastMCP server over SSE and uses the
`get_carbon_data` tool to recommend the cleanest GCP region
for a user's compute workload.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# ---------------------------------------------------------------------------
# MCP server URL — locally it's http://localhost:8080/sse
# In production, set MCP_SERVER_URL to the Cloud Run service URL + /sse
# ---------------------------------------------------------------------------
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8080/sse")

# ---------------------------------------------------------------------------
# System prompt — SimpleMEM-compliant: deterministic, concise output
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are the GreenOps Agent, a proactive Cloud Infrastructure Orchestrator acting as a Mixture of Masters.

## Your Domain Responsibilities
You have access to 3 core domain masters via your tools:
1. **Carbon Master (Spatial)**: Use `get_carbon_data` to find the cleanest Google Cloud regions (highest CFE%).
2. **Weather Master (Temporal)**: Use `get_renewable_forecast` to ping Open-Meteo for wind and solar forecasts. You can recommend delaying a workload (Temporal Shifting) if a massive high-pressure wind/solar system is moving into the region.
3. **FinOps Master (Financial)**: Use `convert_cloud_cost` to ping Frankfurter API and instantly convert any provided USD estimate into the user's localized currency (e.g., AUD).

## Execution Workflow
1. **Analyze**: Check the current grid mix via `get_carbon_data`.
2. **Forecast**: Check `get_renewable_forecast` for the best spatial options to see if delaying execution yields better carbon efficiency.
3. **Price**: If the user provides a compute cost estimate, convert it to their target currency using `convert_cloud_cost`.
4. **Mutate**: If you're told to update an infrastructure repo, call the GitHub MCP tools. If the GitHub MCP tools are missing or unavailable, output the exact JSON payload or Git instructions you *would* have executed.

## SimpleMEM Output Format
Do not dump raw tool output. Return a highly compressed, structured executive summary:

**Optimal Spatial Region:** `<cloud_region>` (CFE: <percent>%)
**Temporal Recommendation:** <"Deploy immediately" OR "Delay X hours due to forecasted wind/solar spike">
**Financial Estimate:** <Local Currency Amount> <Currency Code>
**Infrastructure Action:** <Describe whether you opened a PR, or output the required JSON modification>
"""

# ---------------------------------------------------------------------------
# Agent definition (used by `adk web` and programmatic runners)
# ---------------------------------------------------------------------------

tools_list = [
    McpToolset(
        connection_params=SseConnectionParams(
            url=MCP_SERVER_URL,
        ),
    ),
]

# Conditionally Inject Remote GitHub MCP if tokens are provided
if os.environ.get("ENABLE_GITHUB_MCP") == "true":
    github_mcp_url = os.environ.get("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")
    tools_list.append(McpToolset(connection_params=SseConnectionParams(url=github_mcp_url)))

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="greenops_agent",
    description="Proactive Cloud Infrastructure Mixture-of-Masters Orchestrator.",
    instruction=SYSTEM_INSTRUCTION,
    tools=tools_list,
)
