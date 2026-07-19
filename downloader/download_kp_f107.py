"""
Downloads and processes the GFZ Potsdam combined Kp / ap / Ap / SN / F10.7 file.

Source (one line per UT day, updated daily, data since 1932):
    https://kp.gfz.de/fileadmin/files_for_gfz_cms/Kp_ap_Ap_SN_F107_since_1932.txt

Columns (blank separated, fixed width, see format doc:
https://kp.gfz.de/app/format/Kp_ap_Ap_SN_F107_format.txt):

    YYYY MM DD days days_m BSR dB
    Kp1 Kp2 Kp3 Kp4 Kp5 Kp6 Kp7 Kp8      (8 x three-hourly Kp)
    ap1 ap2 ap3 ap4 ap5 ap6 ap7 ap8      (8 x three-hourly ap)
    Ap SN F10.7obs F10.7adj D

    D: 0 = Kp/SN preliminary, 1 = Kp definitive/SN preliminary,
       2 = Kp and SN definitive.
    Missing data is coded as -1.

Output:
    data/raw/kp_f107/Kp_ap_Ap_SN_F107_since_1932.txt   (raw file, untouched)
    data/processed/kp_f107_daily.csv                    for START_DATE..END_DATE
        columns: date, kp_mean, ap_daily, ssn, f107_obs, f107_adj, def_flag
"""

from pathlib import Path
from datetime import date

import requests
import pandas as pd
import numpy as np

# --------------------------------------------------
# Config
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw" / "kp_f107"
RAW_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / "Kp_ap_Ap_SN_F107_since_1932.txt"
OUTPUT_FILE = PROCESSED_DIR / "kp_f107_daily.csv"

URL = "https://kp.gfz.de/fileadmin/files_for_gfz_cms/Kp_ap_Ap_SN_F107_since_1932.txt"

START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)

MISSING = -1


# --------------------------------------------------
# Step 1: Download
# --------------------------------------------------
def download():
    print(f"Downloading {URL}")
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    RAW_FILE.write_bytes(r.content)
    print(f"Saved -> {RAW_FILE} ({len(r.content)} bytes)")


# --------------------------------------------------
# Step 2: Parse
# --------------------------------------------------
def parse():
    rows = []

    with open(RAW_FILE, "r", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue

            parts = line.split()

            # YYYY MM DD days days_m BSR dB
            # + 8 Kp + 8 ap + Ap SN F10.7obs F10.7adj D  == 7 + 8 + 8 + 5 = 28 fields
            if len(parts) < 28:
                continue

            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            kp_values = [float(x) for x in parts[7:15]]
            ap_values = [float(x) for x in parts[15:23]]

            ap_daily = float(parts[23])
            ssn = float(parts[24])
            f107_obs = float(parts[25])
            f107_adj = float(parts[26])
            def_flag = int(parts[27])

            rows.append(
                {
                    "date": pd.Timestamp(year=year, month=month, day=day),
                    "kp_mean": np.mean(kp_values),
                    "ap_daily": ap_daily if ap_daily != MISSING else np.nan,
                    "ssn": ssn if ssn != MISSING else np.nan,
                    "f107_obs": f107_obs if f107_obs != MISSING else np.nan,
                    "f107_adj": f107_adj if f107_adj != MISSING else np.nan,
                    "def_flag": def_flag,
                }
            )

    df = pd.DataFrame(rows)

    mask = (df["date"] >= pd.Timestamp(START_DATE)) & (
        df["date"] <= pd.Timestamp(END_DATE)
    )
    df = df.loc[mask].sort_values("date").reset_index(drop=True)

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    download()
    df = parse()

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(OUTPUT_FILE, index=False)

    expected_days = (END_DATE - START_DATE).days + 1

    print()
    print(f"Rows: {len(df)}  (expected {expected_days})")
    print("Missing values per column:")
    print(df.isna().sum())
    print(f"Saved -> {OUTPUT_FILE}")
    print()
    print(df.head())
    print(df.tail())
