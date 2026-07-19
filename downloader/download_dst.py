"""
Downloads and processes the Kyoto WDC Provisional Dst index.

2022-01 through 2024-12 all fall inside the "Provisional Dst" range
(2021/01 - 2025/06), so we only need one data source for the whole
project window. (Final Dst only goes up to 2020, Real-time/Quicklook
only kicks in after Provisional runs out.)

Source (one file per month):
    https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/{YYYYMM}/dst{yy}{mm}.for.request

Each file uses the IAGA2002/WDC line format, one line per day, e.g.:

    DST2201*01PPX120   0   6  -3  -7 -13 -21 -23 -17 -16 -17 -13 -12
    -11 -10 -11 -10  -7  -7 -10 -13 -12 -12 -10 -10  -8 -11

Breaking a line down:
    DST           index code
    22            year (2-digit)
    01            month
    *             century marker
    01            day of month
    PPX120        station/version code (not needed)
    0             leading filler value
    <24 values>   hourly Dst in nT
    <1 value>     daily mean, already rounded to the nearest integer
                   by Kyoto -- used here only as a cross-check against
                   our own nanmean of the 24 hourly values.

Missing hourly values are coded as large sentinel numbers (>= 9999 or
<= -9999) -- treated as NaN here.

Output:
    data/raw/dst/dst{yy}{mm}.for.request   (raw monthly files, untouched)
    data/processed/dst_daily.csv           (date, dst_daily_mean) for
                                            START_DATE..END_DATE
"""

import re
import time
from pathlib import Path
from datetime import date
from calendar import monthrange

import requests
import pandas as pd
import numpy as np

# --------------------------------------------------
# Config
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw" / "dst"
RAW_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "dst_daily.csv"

BASE_URL = "https://wdc.kugi.kyoto-u.ac.jp/dst_provisional"

START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)

MISSING_THRESHOLD = 9999

# Day-of-month sits right after the '*' century marker, e.g. "DST2201*01"
DAY_RE = re.compile(r"\*(\d{2})")


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def month_range(start, end):
    """Yield (year, month) tuples from start to end inclusive."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def raw_path(year, month):
    yy = str(year)[2:]
    return RAW_DIR / f"dst{yy}{month:02d}.for.request"


def build_url(year, month):
    yy = str(year)[2:]
    return f"{BASE_URL}/{year}{month:02d}/dst{yy}{month:02d}.for.request"


# --------------------------------------------------
# Step 1: Download (one file per month, skips existing)
# --------------------------------------------------
def download_all():
    session = requests.Session()

    for year, month in month_range(START_DATE, END_DATE):
        out = raw_path(year, month)

        if out.exists():
            print(f"[Skip] {out.name} already downloaded")
            continue

        url = build_url(year, month)
        try:
            r = session.get(url, timeout=60)
            r.raise_for_status()
            out.write_bytes(r.content)
            print(f"[Downloaded] {out.name}")
        except Exception as e:
            print(f"[FAILED] {year}-{month:02d} : {e}")

        time.sleep(0.5)  # be polite to the server


# --------------------------------------------------
# Step 2: Parse one monthly file
# --------------------------------------------------
def parse_month(year, month):
    path = raw_path(year, month)
    if not path.exists():
        return []

    n_days = monthrange(year, month)[1]

    with open(path, "r", errors="ignore") as f:
        lines = f.readlines()

    records = []

    for line in lines:
        if not line.startswith("DST"):
            continue

        day_match = DAY_RE.search(line[:12])
        if not day_match:
            continue

        day = int(day_match.group(1))
        if not (1 <= day <= n_days):
            continue

        nums = re.findall(r"-?\d+", line)

        # The line is: header digits ... leading filler, 24 hourly
        # values, then a trailing pre-rounded daily mean. Reading from
        # the end sidesteps the variable-length header prefix entirely.
        if len(nums) < 25:
            print(f"[Parse warning] {path.name} day {day}: only {len(nums)} numbers found, skipping")
            continue

        hourly_raw = nums[-25:-1]
        file_mean = float(nums[-1])

        values = np.array([float(x) for x in hourly_raw])
        values[np.abs(values) >= MISSING_THRESHOLD] = np.nan

        computed_mean = np.nanmean(values)

        # Cross-check against Kyoto's own rounded daily mean
        if not np.isnan(computed_mean) and abs(round(computed_mean) - file_mean) > 1:
            print(
                f"[Mean mismatch] {path.name} day {day}: "
                f"computed={computed_mean:.3f} file={file_mean}"
            )

        records.append(
            {
                "date": pd.Timestamp(year=year, month=month, day=day),
                "dst_daily_mean": computed_mean,
                "n_missing_hours": int(np.isnan(values).sum()),
            }
        )

    return records


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    download_all()

    all_records = []
    for year, month in month_range(START_DATE, END_DATE):
        all_records.extend(parse_month(year, month))

    df = pd.DataFrame(all_records).sort_values("date").reset_index(drop=True)

    expected_days = (END_DATE - START_DATE).days + 1

    print()
    print(f"Rows: {len(df)}  (expected {expected_days})")

    if len(df) != expected_days:
        got_dates = set(df["date"].dt.strftime("%Y-%m-%d"))
        all_dates = set(
            pd.date_range(START_DATE, END_DATE).strftime("%Y-%m-%d")
        )
        missing = sorted(all_dates - got_dates)
        print(f"Missing {len(missing)} dates, e.g.: {missing[:10]}")

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved -> {OUTPUT_FILE}")
    print()
    print(df.head())
    print(df.tail())