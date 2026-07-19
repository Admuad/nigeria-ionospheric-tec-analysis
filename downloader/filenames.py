def candidate_filenames(year: int, doy: int):
    yy = str(year)[2:]

    # Legacy CODE naming (available until 2022 DOY 330)
    if year == 2022 and doy <= 330:
        yield f"codg{doy:03d}0.{yy}i.Z"

    # New MGEX naming (from 2022 DOY 331 onwards)
    yield (
        f"COD0OPSFIN_"
        f"{year}{doy:03d}0000_"
        f"01D_01H_GIM.INX.gz"
    )