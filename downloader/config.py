from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent

# Data directory
IONEX_ROOT = ROOT / "data" / "raw" / "ionex"
IONEX_ROOT.mkdir(parents=True, exist_ok=True)

# Download range
START_YEAR = 2022
END_YEAR = 2024

# Parallel downloads
MAX_DOWNLOADS = 3

# Network
RETRIES = 5
TIMEOUT = 120  # seconds
BACKOFF_FACTOR = 2

# Download source
BASE_URL = "https://cddis.nasa.gov/archive/gnss/products/ionex"