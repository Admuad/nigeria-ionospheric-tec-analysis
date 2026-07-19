"""
Project Configuration
Investigation of Solar Activity Effects on Ionospheric TEC
Study Location: Abuja, Nigeria
"""

# ==========================
# Study Location
# ==========================

ABUJA_LAT = 9.08
ABUJA_LON = 7.40

# ==========================
# TEC Grid
# ==========================

LAT_START = 87.5
LAT_END = -87.5
LAT_STEP = -2.5

LON_START = -180.0
LON_END = 180.0
LON_STEP = 5.0

# ==========================
# IONEX
# ==========================

MAPS_PER_DAY = 25
N_LAT = 71
N_LON = 73

# ==========================
# Project Paths
# ==========================

IONEX_FOLDER = "../data/ionex"

OUTPUT_FOLDER = "../data/processed"

OUTPUT_FILE = "tec_daily.csv"