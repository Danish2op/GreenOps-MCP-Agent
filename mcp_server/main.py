import os
import requests
from fastmcp import FastMCP
from mcp_server.bq_client import get_cfe_data
from mcp_server.geospatial import get_region_coordinates

mcp = FastMCP("greenops-mcp")

@mcp.tool
def get_renewable_forecast(region: str) -> dict:
    """Fetch 7-day wind speed and cloud cover forecasts for a Google Cloud region.
    
    This is critical for Temporal Workload Shifting. Lower cloud cover means higher solar generation.
    Higher wind speed means higher wind generation.
    
    Args:
        region: The Google Cloud region name (e.g. "europe-north2").
        
    Returns:
        A dictionary containing daily forecast summaries, or an error if the region isn't supported.
    """
    coords = get_region_coordinates(region)
    if not coords:
        return {"error": f"Coordinates not found for region: {region}"}
    
    lat, lon = coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=cloudcover_mean,windspeed_10m_max&timezone=auto"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Format the daily data concisely
        daily = data.get("daily", {})
        times = daily.get("time", [])
        cloud_cover = daily.get("cloudcover_mean", [])
        wind_speed = daily.get("windspeed_10m_max", [])
        
        forecasts = []
        for i in range(len(times)):
            forecasts.append({
                "date": times[i],
                "cloud_cover_percent": cloud_cover[i] if i < len(cloud_cover) else None,
                "wind_speed_kmh": wind_speed[i] if i < len(wind_speed) else None
            })
            
        return {
            "region": region,
            "latitude": lat,
            "longitude": lon,
            "forecasts": forecasts
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def convert_cloud_cost(amount: float, from_currency: str = "USD", to_currency: str = "AUD") -> dict:
    """Convert a financial cost from one currency to another using current exchange rates.
    
    Use this for FinOps localization when a user requests prices in their local currency.
    
    Args:
        amount: The monetary amount (e.g. 45.0)
        from_currency: 3-letter currency code (default: USD)
        to_currency: 3-letter currency code (default: AUD)
        
    Returns:
        JSON with the converted amount and the rate.
    """
    # Frankfurter API for completely free, unauthenticated forex rates
    url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": data.get("rates", {}).get(to_currency),
            "converted_currency": to_currency,
            "date": data.get("date")
        }
    except Exception as e:
        return {"error": str(e)}


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
