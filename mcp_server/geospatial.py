"""Geospatial coordinates for Google Cloud Regions to enable Open-Meteo queries."""

# Static mapping covering major GCP regions. (Latitude, Longitude)
GCP_REGION_COORDINATES = {
    # Americas
    "us-east1": (33.1972, -80.0131),         # South Carolina
    "us-east4": (39.0438, -77.4874),         # Northern Virginia
    "us-central1": (41.2619, -95.8608),      # Iowa
    "us-west1": (45.5946, -121.1787),        # Oregon
    "us-west2": (34.0522, -118.2437),        # Los Angeles
    "us-west3": (40.7608, -111.8910),        # Salt Lake City
    "us-west4": (36.1699, -115.1398),        # Las Vegas
    "us-south1": (32.7767, -96.7970),        # Dallas
    "northamerica-northeast1": (45.5017, -73.5673), # Montreal
    "northamerica-northeast2": (43.6532, -79.3832), # Toronto
    "southamerica-east1": (-23.5505, -46.6333),     # Sao Paulo
    "southamerica-west1": (-33.4489, -70.6693),     # Santiago

    # Europe
    "europe-west1": (50.4485, 3.8188),       # Belgium
    "europe-west2": (51.5074, -0.1278),      # London
    "europe-west3": (50.1109, 8.6821),       # Frankfurt
    "europe-west4": (53.4386, 6.8355),       # Eemshaven, Netherlands
    "europe-west6": (47.3769, 8.5417),       # Zurich
    "europe-west8": (45.4642, 9.1900),       # Milan
    "europe-west9": (48.8566, 2.3522),       # Paris
    "europe-west12": (45.0703, 7.6869),      # Turin
    "europe-north1": (60.5693, 27.1938),     # Hamina, Finland
    "europe-north2": (60.1695, 24.9354),     # Helsinki, Finland (approx bounds)
    "europe-southwest1": (40.4168, -3.7038), # Madrid

    # Asia Pacific
    "asia-east1": (24.0512, 120.5161),       # Taiwan
    "asia-east2": (22.3193, 114.1694),       # Hong Kong
    "asia-northeast1": (35.6895, 139.6917),  # Tokyo
    "asia-northeast2": (34.6937, 135.5023),  # Osaka
    "asia-northeast3": (37.5665, 126.9780),  # Seoul
    "asia-south1": (19.0760, 72.8777),       # Mumbai
    "asia-south2": (28.6139, 77.2090),       # Delhi
    "asia-southeast1": (1.3521, 103.8198),   # Singapore
    "asia-southeast2": (-6.2088, 106.8456),  # Jakarta
    "australia-southeast1": (-33.8688, 151.2093),   # Sydney
    "australia-southeast2": (-37.8136, 144.9631),   # Melbourne

    # Middle East & Africa
    "me-west1": (32.0853, 34.7818),          # Tel Aviv
    "me-central1": (25.2769, 51.5200),       # Doha
    "me-central2": (26.0667, 50.5577),       # Dammam
    "africa-south1": (-26.2041, 28.0473),    # Johannesburg
}

def get_region_coordinates(region_name: str) -> tuple[float, float] | None:
    """Returns the (latitude, longitude) for a standard GCP region string. None if unknown."""
    return GCP_REGION_COORDINATES.get(region_name.lower())
