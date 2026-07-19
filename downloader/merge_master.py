"""
Merges the four processed datasets into one master dataframe for
correlation analysis / modeling.

Inputs (all in data/processed/):
    tec_abuja_2022_2024.csv   -> date, daily_mean_tec, hour_00..hour_24
    ssn_daily.csv              -> date, ssn, def_flag
    kp_f107_daily.csv          -> date, kp_mean, ap_daily, ssn, f107_obs,
                                   f107_adj, def_flag
    dst_daily.csv              -> date, dst_daily_mean, n_missing_hours

Output:
    data/processed/master_dataset.csv
        date, daily_mean_tec, kp_mean, ap_daily, dst_daily_mean,
        ssn, f107_obs, f107_adj

Note: both SILSO and the GFZ file provide a sunspot number. We keep
SILSO's ssn as the primary "ssn" column (project spec names SILSO
explicitly) and drop the GFZ duplicate after using it to cross-check.
"""

from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

TEC_FILE = PROCESSED_DIR / "tec_abuja_2022_2024.csv"
SSN_FILE = PROCESSED_DIR / "ssn_daily.csv"
KP_F107_FILE = PROCESSED_DIR / "kp_f107_daily.csv"
DST_FILE = PROCESSED_DIR / "dst_daily.csv"

OUTPUT_FILE = PROCESSED_DIR / "master_dataset.csv"


def load(path, name):
    if not path.exists():
        raise FileNotFoundError(
            f"{name} not found at {path}. Run its downloader first."
        )
    df = pd.read_csv(path, parse_dates=["date"])
    return df


if __name__ == "__main__":
    tec = load(TEC_FILE, "TEC dataset")[["date", "daily_mean_tec"]]
    ssn = load(SSN_FILE, "SSN dataset")[["date", "ssn"]]
    kp = load(KP_F107_FILE, "Kp/F10.7 dataset")[
        ["date", "kp_mean", "ap_daily", "f107_obs", "f107_adj", "ssn"]
    ].rename(columns={"ssn": "ssn_gfz"})
    dst = load(DST_FILE, "Dst dataset")[["date", "dst_daily_mean"]]

    df = tec.merge(ssn, on="date", how="left")
    df = df.merge(kp, on="date", how="left")
    df = df.merge(dst, on="date", how="left")

    # Cross-check: SILSO ssn vs GFZ's copy of SILSO ssn should agree
    # (GFZ ingests the same SILSO series, occasionally a version behind
    # for the most recent ~months, hence the separate cross-check
    # rather than silently trusting one source).
    diff = (df["ssn"] - df["ssn_gfz"]).abs()
    mismatches = df.loc[diff > 0.5, ["date", "ssn", "ssn_gfz"]]

    df = df.drop(columns=["ssn_gfz"])
    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Merged rows: {len(df)}")
    print()
    print("Missing values per column:")
    print(df.isna().sum())
    print()
    if len(mismatches):
        print(
            f"SSN mismatch (SILSO vs GFZ) on {len(mismatches)} days "
            f"(usually just the most recent provisional months):"
        )
        print(mismatches.head(10))
    else:
        print("SSN cross-check: SILSO and GFZ agree on every day.")
    print()
    print(f"Saved -> {OUTPUT_FILE}")
    print()
    print(df.head())
    print(df.tail())
