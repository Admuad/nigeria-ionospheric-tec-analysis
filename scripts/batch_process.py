from pathlib import Path

import pandas as pd

from extract_tec import extract_daily_tec, extract_date


ROOT = Path(__file__).resolve().parent.parent

IONEX_ROOT = ROOT / "data" / "raw" / "ionex"

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tec_abuja_2022_2024.csv"

FAILED_FILE = OUTPUT_DIR / "failed_files.txt"


records = []
failed = []


files = sorted(
    list(IONEX_ROOT.rglob("*.22i")) +
    list(IONEX_ROOT.rglob("*.INX"))
)

print(f"Found {len(files)} IONEX files")


for idx, file in enumerate(files, start=1):

    try:

        hourly, daily = extract_daily_tec(file)

        if len(hourly) != 25:
            raise ValueError(
                f"Expected 25 maps, got {len(hourly)}"
            )

        record = {
            "date": extract_date(file),
            "daily_mean_tec": daily
        }

        for h, value in enumerate(hourly):
            record[f"hour_{h:02d}"] = value

        records.append(record)

        print(f"[{idx}/{len(files)}] OK  {file.name}")

    except Exception as e:

        failed.append(f"{file.name} : {e}")

        print(f"[{idx}/{len(files)}] FAIL {file.name}")


df = pd.DataFrame(records)

df = df.sort_values("date")

df.to_csv(OUTPUT_FILE, index=False)

print()
print(f"Saved {len(df)} days")
print(f"CSV -> {OUTPUT_FILE}")


if failed:

    with open(FAILED_FILE, "w") as f:

        for line in failed:
            f.write(line + "\n")

    print(f"{len(failed)} files failed")
    print(f"Log -> {FAILED_FILE}")

else:

    print("No failed files.")