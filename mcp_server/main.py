"""GreenOps FastMCP Server — exposes a single `get_carbon_data` tool.

Runs over HTTP/SSE for Cloud Run compatibility.
"""

import os
from fastmcp import FastMCP
from mcp_server.bq_client import get_cfe_data

mcp = FastMCP("greenops-mcp")


@mcp.tool
def get_carbon_data(
    regions: list[str] | None = None,
    year: int | None = None,
) -> list[dict]:
    """Fetch carbon-free energy (CFE%) data for Google Cloud regions.

    Returns regions ranked by CFE percentage (highest = cleanest).

    Args:
        regions: Optional list of GCP region names to filter
                 (e.g. ["us-central1", "europe-west1"]).
                 If omitted, returns all Cloud regions.
        year:    Optional year. Defaults to the most recent year in the dataset.

    Returns:
        A ranked list of dicts with keys:
        - cloud_region: GCP region name
        - location: Friendly location name
        - google_cfe: Carbon-Free Energy percentage (0-1 scale)
        - grid_carbon_intensity: Grid emissions factor
        - year: Data year
    """
    return get_cfe_data(regions=regions, year=year)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
