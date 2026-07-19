"""
Download CODE Global Ionosphere Maps (IONEX)

Period:
2022 - 2024

Author:
TEC Project
"""

import os
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from unlzw3 import unlzw


BASE_URL = (
    "https://cddis.nasa.gov/archive/gnss/products/ionex"
)

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 12, 31)

OUTPUT = "../data/ionex"


def download_file(url, destination):

    r = requests.get(url, stream=True)

    if r.status_code != 200:
        return False

    with open(destination, "wb") as f:

        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    return True


def decompress_Z(zfile, outfile):

    with open(zfile, "rb") as f:
        compressed = f.read()

    data = unlzw(compressed)

    with open(outfile, "wb") as f:
        f.write(data)


def main():

    current = START_DATE

    total_days = (END_DATE - START_DATE).days + 1

    pbar = tqdm(total=total_days)

    while current <= END_DATE:

        year = current.year
        yy = str(year)[2:]
        doy = current.timetuple().tm_yday

        folder = os.path.join(OUTPUT, str(year))
        os.makedirs(folder, exist_ok=True)

        ionex = f"codg{doy:03d}0.{yy}i"
        compressed = ionex + ".Z"

        final_file = os.path.join(folder, ionex)

        if os.path.exists(final_file):
            current += timedelta(days=1)
            pbar.update(1)
            continue

        url = (
            f"{BASE_URL}/{year}/{doy:03d}/"
            f"{compressed}"
        )

        zpath = os.path.join(folder, compressed)

        ok = download_file(url, zpath)

        if ok:

            try:

                decompress_Z(zpath, final_file)

                os.remove(zpath)

            except Exception as e:

                print(f"\nFailed: {ionex}")
                print(e)

        else:

            print(f"\nMissing: {compressed}")

        current += timedelta(days=1)

        pbar.update(1)

    pbar.close()

    print("\nFinished.")


if __name__ == "__main__":
    main()