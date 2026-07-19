from queue import Queue
import threading

from config import (
    START_YEAR,
    END_YEAR,
    MAX_DOWNLOADS,
)

from filenames import candidate_filenames
from scanner import scan_existing
from workers import (
    worker,
    extractor,
    extract_queue,
)

# -----------------------------
# Build task queue
# -----------------------------

queue = Queue()

completed = scan_existing()

for year in range(START_YEAR, END_YEAR + 1):

    days = 366 if year % 4 == 0 else 365

    for doy in range(1, days + 1):

        names = [
            name.replace(".Z", "").replace(".gz", "").lower()
            for name in candidate_filenames(year, doy)
        ]

        if any((year, name) in completed for name in names):
            continue

        queue.put((year, doy))

print(f"Tasks queued: {queue.qsize()}")

# -----------------------------
# Start extractor
# -----------------------------

extract_thread = threading.Thread(
    target=extractor,
    daemon=True,
)
extract_thread.start()

# -----------------------------
# Start download workers
# -----------------------------

workers = []

for _ in range(MAX_DOWNLOADS):

    t = threading.Thread(
        target=worker,
        args=(queue,),
        daemon=True,
    )

    t.start()
    workers.append(t)

# -----------------------------
# Wait for downloads
# -----------------------------

queue.join()

for _ in workers:
    queue.put(None)

for t in workers:
    t.join()

# -----------------------------
# Wait for extraction
# -----------------------------

extract_queue.join()

extract_queue.put(None)
extract_thread.join()

print("Download complete.")