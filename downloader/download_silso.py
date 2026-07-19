"""
Downloads and processes the SILSO daily total sunspot number.

Source:
    https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.csv

Format (semicolon-separated):
    year ; month ; day ; decimal_year ; SN ; SN_stderr ; n_obs ; def_flag

    SN = -1 means missing value for that day.
    def_flag: 1 = definitive, 0 = still provisional.

Output:
    data/raw/silso/SN_d_tot_V2.0.csv   (raw file, untouched)
    data/processed/ssn_daily.csv       (date, ssn) for START_DATE..END_DATE
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

RAW_DIR = ROOT / "data" / "raw" / "silso"
RAW_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / "SN_d_tot_V2.0.csv"
OUTPUT_FILE = PROCESSED_DIR / "ssn_daily.csv"

URL = "https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.csv"

START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)


# --------------------------------------------------
# Step 1: Download
# --------------------------------------------------
def download():
    print(f"Downloading {URL}")
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    RAW_FILE.write_bytes(r.content)
    print(f"Saved -> {RAW_FILE} ({len(r.content)} bytes)")


# --------------------------------------------------
# Step 2: Parse
# --------------------------------------------------
def parse():
    df = pd.read_csv(
        RAW_FILE,
        sep=";",
        header=None,
        names=[
            "year",
            "month",
            "day",
            "decimal_year",
            "ssn",
            "ssn_stderr",
            "n_obs",
            "def_flag",
        ],
        usecols=range(8),
    )

    df["date"] = pd.to_datetime(df[["year", "month", "day"]])

    # -1 means missing
    df["ssn"] = df["ssn"].replace(-1, np.nan)

    df = df[["date", "ssn", "def_flag"]]

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
    print(f"Missing SSN values: {df['ssn'].isna().sum()}")
    print(f"Provisional rows (def_flag == 0): {(df['def_flag'] == 0).sum()}")
    print(f"Saved -> {OUTPUT_FILE}")
    print()
    print(df.head())
    print(df.tail())
