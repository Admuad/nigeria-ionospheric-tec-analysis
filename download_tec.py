import os
import math
import calendar
import requests
from tqdm import tqdm
from unlzw3 import unlzw
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

START_YEAR = 2022
END_YEAR = 2024

RAW_FOLDER = "data/raw/ionex"
os.makedirs(RAW_FOLDER, exist_ok=True)

# Earthdata session using .netrc automatically
session = requests.Session()
session.trust_env = True

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
)

session.mount("https://", HTTPAdapter(max_retries=retries))

downloaded = 0
failed = []

for year in range(START_YEAR, END_YEAR + 1):

    yy = str(year)[2:]
    days = 366 if calendar.isleap(year) else 365

    year_folder = os.path.join(RAW_FOLDER, str(year))
    os.makedirs(year_folder, exist_ok=True)

    for doy in range(1, days + 1):

        filename = f"codg{doy:03d}0.{yy}i.Z"

        url = (
            f"https://cddis.nasa.gov/archive/"
            f"gnss/products/ionex/{year}/{doy:03d}/{filename}"
        )

        z_path = os.path.join(year_folder, filename)
        i_path = z_path[:-2]  # remove .Z

        # Skip if already extracted
        if os.path.exists(i_path):
            continue

        print(f"[{year} DOY {doy:03d}] {filename}")

        try:
            r = session.get(url, stream=True, allow_redirects=True, timeout=60)

            if r.status_code != 200:
                failed.append(filename)
                print(f"  Missing ({r.status_code})")
                continue

            content_type = r.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                failed.append(filename)
                print("  Received HTML login page")
                continue

            total = int(r.headers.get("content-length", 0))

            with open(z_path, "wb") as f:
                for chunk in tqdm(
                    r.iter_content(chunk_size=8192),
                    total=max(math.ceil(total / 8192), 1),
                    unit="KB",
                    leave=False,
                ):
                    if chunk:
                        f.write(chunk)

            # Decompress .Z → .i
            with open(z_path, "rb") as f:
                compressed = f.read()

            decompressed = unlzw(compressed)

            with open(i_path, "wb") as f:
                f.write(decompressed)

            os.remove(z_path)

            downloaded += 1

        except Exception as e:
            failed.append(filename)
            print(f"  Error: {e}")

print("\n============================")
print("DOWNLOAD COMPLETE")
print("============================")
print(f"Downloaded: {downloaded}")
print(f"Failed: {len(failed)}")

if failed:
    with open("failed_downloads.txt", "w") as f:
        for item in failed:
            f.write(item + "\n")
    print("Failed list saved to failed_downloads.txt")