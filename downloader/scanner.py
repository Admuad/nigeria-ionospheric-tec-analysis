from config import IONEX_ROOT


def scan_existing():
    """
    Returns a set of (year, filename) for every extracted IONEX file
    already present on disk.
    """

    completed = set()

    if not IONEX_ROOT.exists():
        return completed

    for year_dir in IONEX_ROOT.iterdir():

        if not year_dir.is_dir():
            continue

        try:
            year = int(year_dir.name)
        except ValueError:
            continue

        for file in year_dir.iterdir():

            if not file.is_file():
                continue

            name = file.name.lower()

            # Ignore compressed files and partial downloads
            if (
                name.endswith(".z")
                or name.endswith(".gz")
                or name.endswith(".part")
            ):
                continue

            # Keep only extracted IONEX files
            if (
                name.endswith(".i")
                or name.endswith(".inx")
            ):
                completed.add((year, name))

    return completed