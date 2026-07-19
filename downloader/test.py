from pathlib import Path

path = Path("../data/raw/dst/dst2201.for.request")
text = path.read_text(errors="ignore")

print(repr(text[:500]))
print("---")
print(text[:2000])