"""BigQuery client for querying the Google Cloud CFE public dataset.

RLM Pattern: All filtering and aggregation happen here via SQL.
Only compact (region, cfe_pct, grid_carbon_intensity, year) tuples
are returned to the MCP tool — never raw rows.
"""

import os
from google.cloud import bigquery

# The public dataset table for Google Cloud carbon-free energy scores
_TABLE = "bigquery-public-data.google_cfe.datacenter_cfe"

# Reuse a single client across invocations (Cloud Run container reuse)
_client: bigquery.Client | None = None


def _get_client() -> bigquery.Client:
    """Lazily initialise the BigQuery client using ADC."""
    global _client
    if _client is None:
        project = os.environ.get("GCP_PROJECT_ID")
        _client = bigquery.Client(project=project)
    return _client


def get_cfe_data(
    regions: list[str] | None = None,
    year: int | None = None,
) -> list[dict]:
    """Return CFE scores ranked by google_cfe descending.

    Args:
        regions: Optional list of Cloud Region names to filter
                 (e.g. ["us-central1", "europe-west1"]).
        year:    Optional year to filter. Defaults to the latest year
                 available in the dataset.

    Returns:
        List of dicts with keys: cloud_region, location, google_cfe,
        grid_carbon_intensity, year.  Sorted by google_cfe DESC.
    """
    client = _get_client()

    conditions = [
        "cloud_region != 'non-cloud-data-center'",
        "google_cfe IS NOT NULL",
    ]
    params: list[bigquery.ScalarQueryParameter] = []

    if regions:
        placeholders = ", ".join(f"@r{i}" for i in range(len(regions)))
        conditions.append(f"cloud_region IN ({placeholders})")
        for i, r in enumerate(regions):
            params.append(
                bigquery.ScalarQueryParameter(f"r{i}", "STRING", r)
            )

    if year is not None:
        conditions.append("year = @yr")
        params.append(bigquery.ScalarQueryParameter("yr", "INT64", year))
    else:
        # Sub-query to grab the latest year
        conditions.append(f"year = (SELECT MAX(year) FROM `{_TABLE}`)")

    where = " AND ".join(conditions)

    sql = f"""
        SELECT
            cloud_region,
            location,
            ROUND(google_cfe, 4) AS google_cfe,
            ROUND(grid_carbon_intensity, 4) AS grid_carbon_intensity,
            year
        FROM `{_TABLE}`
        WHERE {where}
        ORDER BY google_cfe DESC
    """

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = client.query(sql, job_config=job_config).result()

    return [dict(row) for row in rows]
