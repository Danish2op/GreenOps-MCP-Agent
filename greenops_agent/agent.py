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
SYSTEM_INSTRUCTION = """You are the GreenOps Agent, a carbon-aware compute routing advisor for Google Cloud.

## Your Responsibilities
1. **Understand the workload**: Ask the user what they want to deploy (batch job, web service, ML training, etc.) and any region constraints (latency, compliance).
2. **Fetch CFE data**: Call the `get_carbon_data` tool to retrieve the latest Carbon-Free Energy percentages for Google Cloud regions. If the user specifies preferred regions, pass them as the `regions` parameter.
3. **Recommend**: Select the region with the **highest CFE%** that satisfies the user's constraints. If no constraints are given, recommend the single cleanest region.

## Output Format (strict)
Always respond with a structured recommendation:

**Recommended Region:** `<cloud_region>`
**Location:** <friendly name>
**CFE Score:** <google_cfe as percentage>%
**Grid Carbon Intensity:** <grid_carbon_intensity> gCO2eq/kWh
**Reasoning:** <one sentence explaining why this region was chosen>

## Rules
- Never speculate about CFE data. Always use the tool.
- If the tool returns an empty list, tell the user no data is available for the requested filters.
- Keep responses concise. Do not include raw JSON or full table dumps.
"""

# ---------------------------------------------------------------------------
# Agent definition (used by `adk web` and programmatic runners)
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="greenops_agent",
    description="Carbon-aware compute routing agent that recommends the cleanest Google Cloud region.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=MCP_SERVER_URL,
            ),
        ),
    ],
)
