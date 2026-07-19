import re
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np


# Abuja coordinates
ABUJA_LAT = 9.0765
ABUJA_LON = 7.3986

# IONEX grid definition
LAT_START = 87.5
LAT_STEP = -2.5

LON_START = -180.0
LON_STEP = 5.0

N_LAT = 71
N_LON = 73


def lat_to_index(lat):
    return int(round((LAT_START - lat) / abs(LAT_STEP)))


def lon_to_index(lon):
    if lon < 0:
        lon = 360 + lon

    if lon > 180:
        lon -= 360

    return int(round((lon - LON_START) / LON_STEP))


LAT_IDX = lat_to_index(ABUJA_LAT)
LON_IDX = lon_to_index(ABUJA_LON)


def extract_daily_tec(file_path):

    file_path = Path(file_path)

    with open(file_path, "r", errors="ignore") as f:
        lines = f.readlines()

    exponent = -1

    for line in lines:
        if "EXPONENT" in line:
            exponent = int(line[:6])
            break

    scale = 10 ** exponent

    hourly = []

    i = 0

    while i < len(lines):

        if "START OF TEC MAP" not in lines[i]:
            i += 1
            continue

        i += 1

        tec_grid = []

        while i < len(lines):

            line = lines[i]

            if "END OF TEC MAP" in line:
                break

            if "LAT/LON1/LON2/DLON/H" in line:

                i += 1

                row = []

                while i < len(lines):

                    current = lines[i]

                    if (
                        "LAT/LON1/LON2/DLON/H" in current
                        or "END OF TEC MAP" in current
                    ):
                        break

                    nums = [int(x) for x in re.findall(r"-?\d+", current)]

                    row.extend(nums)

                    i += 1

                tec_grid.append(row)

                continue

            i += 1

        tec_grid = np.array(tec_grid, dtype=float)

        tec_grid *= scale

        if tec_grid.shape != (N_LAT, N_LON):
            raise ValueError(
                f"Unexpected TEC grid shape {tec_grid.shape}"
            )

        value = tec_grid[LAT_IDX, LON_IDX]

        if value == 999.9:
            value = np.nan

        hourly.append(value)

        i += 1

    hourly = np.array(hourly)

    if len(hourly) != 25:
        raise ValueError(f"Expected 25 maps, got {len(hourly)}")

    daily = np.nanmean(hourly)

    return hourly, float(daily)


def extract_date(file_path):

    name = Path(file_path).name

    m = re.match(r"codg(\d{3})0\.(\d{2})i", name.lower())

    if m:

        doy = int(m.group(1))
        year = 2000 + int(m.group(2))

    else:

        m = re.search(r"_(\d{4})(\d{3})", name)

        if m is None:
            raise ValueError(f"Cannot parse date from {name}")

        year = int(m.group(1))
        doy = int(m.group(2))

    return (
        datetime(year, 1, 1) +
        timedelta(days=doy - 1)
    ).strftime("%Y-%m-%d")


if __name__ == "__main__":

    import sys

    hourly, daily = extract_daily_tec(sys.argv[1])

    print(hourly)
    print(daily)
    print(extract_date(sys.argv[1]))