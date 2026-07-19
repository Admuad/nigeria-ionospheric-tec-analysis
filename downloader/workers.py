import os
import time
import gzip
import threading
from queue import Queue

import requests
import unlzw3

from config import (
    IONEX_ROOT,
    BASE_URL,
    RETRIES,
    TIMEOUT,
)

from filenames import candidate_filenames

# ----------------------------------------
# Queue for extraction
# ----------------------------------------

extract_queue = Queue()

# ----------------------------------------
# File locks
# ----------------------------------------

_locks = {}
_master_lock = threading.Lock()


def get_lock(path):

    with _master_lock:

        if path not in _locks:
            _locks[path] = threading.Lock()

        return _locks[path]


# ----------------------------------------
# URL builder
# ----------------------------------------

def build_url(year, doy, filename):

    return f"{BASE_URL}/{year}/{doy:03d}/{filename}"


# ----------------------------------------
# Extraction
# ----------------------------------------

def extract_archive(path):

    path = str(path)

    if path.endswith(".gz"):

        out = path[:-3]

        with gzip.open(path, "rb") as fin:
            with open(out, "wb") as fout:
                fout.write(fin.read())

        os.remove(path)

        return

    if path.endswith(".Z"):

        out = path[:-2]

        with open(path, "rb") as fin:
            data = unlzw3.unlzw(fin.read())

        with open(out, "wb") as fout:
            fout.write(data)

        os.remove(path)


def extractor():

    while True:

        item = extract_queue.get()

        if item is None:
            break

        try:

            extract_archive(item)

            print(f"[Extracted] {os.path.basename(item)}")

        except Exception as e:

            print(f"[Extract Error] {item} : {e}")

        finally:

            extract_queue.task_done()


# ----------------------------------------
# Download one day
# ----------------------------------------

def download_day(session, year, doy):

    year_dir = IONEX_ROOT / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    for filename in candidate_filenames(year, doy):

        archive = year_dir / filename
        extracted = year_dir / filename.replace(".gz", "").replace(".Z", "")
        partial = year_dir / (filename + ".part")

        lock = get_lock(str(extracted))

        with lock:

            if extracted.exists():
                return True

            if archive.exists():
                extract_queue.put(archive)
                return True

            if partial.exists():
                partial.unlink()

            url = build_url(year, doy, filename)

            for attempt in range(RETRIES):

                try:

                    response = session.get(
                        url,
                        stream=True,
                        timeout=TIMEOUT,
                    )

                    if response.status_code == 404:
                        break

                    response.raise_for_status()

                    with open(partial, "wb") as f:

                        for chunk in response.iter_content(1024 * 1024):

                            if chunk:
                                f.write(chunk)

                    os.replace(partial, archive)

                    print(f"[Downloaded] {filename}")

                    extract_queue.put(archive)

                    return True

                except Exception as e:

                    print(
                        f"[Retry {attempt+1}/{RETRIES}] {filename} : {e}"
                    )

                    if partial.exists():
                        partial.unlink()

                    time.sleep(2 ** attempt)

    print(f"[Missing] {year}/{doy:03d}")

    return False


# ----------------------------------------
# Worker thread
# ----------------------------------------

def worker(queue):

    session = requests.Session()

    session.trust_env = True

    while True:

        task = queue.get()

        if task is None:
            queue.task_done()
            break

        year, doy = task

        download_day(session, year, doy)

        queue.task_done()