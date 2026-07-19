import numpy as np
from scripts.config import (
    LAT_START,
    LAT_END,
    LAT_STEP,
    LON_START,
    LON_END,
    LON_STEP
)


def read_ionex(filename):
    """
    Reads a CODE IONEX file and returns

    tec_maps : ndarray (25,71,73)
    latitudes
    longitudes
    """

    with open(filename) as f:
        lines = f.readlines()

    exponent = -1

    for line in lines:
        if "EXPONENT" in line:
            exponent = int(line.split()[0])
            break

    maps = []

    i = 0

    while i < len(lines):

        if "START OF TEC MAP" not in lines[i]:
            i += 1
            continue

        # Skip START + EPOCH
        i += 2

        current = []

        for _ in range(71):

            # Skip LAT/LON header
            i += 1

            row = []

            while len(row) < 73:

                nums = []

                for value in lines[i].split():
                    try:
                        nums.append(int(value))
                    except:
                        pass

                row.extend(nums)
                i += 1

            row = row[:73]

            row = [
                np.nan if x == 9999 else x * (10 ** exponent)
                for x in row
            ]

            current.append(row)

        maps.append(current)

        while "END OF TEC MAP" not in lines[i]:
            i += 1

        i += 1

    tec = np.array(maps)

    latitudes = np.arange(
    LAT_START,
    LAT_END + LAT_STEP,
    LAT_STEP
)

    longitudes = np.arange(
    LON_START,
    LON_END + LON_STEP,
    LON_STEP
)

    return tec, latitudes, longitudes