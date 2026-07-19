from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IONEX_ROOT = ROOT / "data" / "raw" / "ionex"

print(next(IONEX_ROOT.rglob("*")))
print(list((IONEX_ROOT / "2022").iterdir())[:10])