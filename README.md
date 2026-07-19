# 🇳🇬 Nigeria Ionospheric Total Electron Content (TEC) Analysis and Prediction

A complete end-to-end research pipeline for downloading, processing, analyzing, and modeling ionospheric Total Electron Content (TEC) over Abuja, Nigeria using Global Ionospheric Maps (GIM), solar activity indices, and geomagnetic indices.

This project was developed as part of a research study investigating the influence of solar and geomagnetic activity on ionospheric TEC and evaluating machine learning techniques for TEC prediction.

---

# Features

- Automatic download of Global Ionospheric Map (IONEX) files from NASA CDDIS
- Support for both legacy (`codg*.22i`) and modern (`COD0OPSFIN*.INX`) IONEX formats
- Parallel downloader with multiple workers
- Automatic extraction and cleanup
- Daily TEC extraction from Global Ionospheric Maps
- Automatic download of:
  - SILSO Sunspot Number (SSN)
  - NOAA F10.7 Solar Flux
  - NOAA Kp Index
  - NOAA Ap Index
  - Kyoto Dst Index
- Dataset merging into a single master dataset
- Exploratory Data Analysis (EDA)
- Statistical analysis
- Multiple Linear Regression
- Neural Network prediction model using TensorFlow/Keras
- Publication-quality visualizations

---

# Study Area

**Location**

Abuja, Nigeria

Approximate Coordinates

- Latitude: **9.0765° N**
- Longitude: **7.3986° E**

Study Period

**1 January 2022 – 31 December 2024**

Total observations:

- **1096 daily records**

---

# Data Sources

## Global Ionospheric Maps (TEC)

Source:

NASA CDDIS

https://cddis.nasa.gov/

Products used:

- COD Final GIM
- Legacy IONEX (.22i)
- Modern IONEX (.INX)

---

## Sunspot Number

SILSO

https://www.sidc.be/SILSO/

---

## Solar Flux (F10.7)

NOAA Space Weather Prediction Center

https://www.swpc.noaa.gov/

---

## Geomagnetic Indices

NOAA

- Kp Index
- Ap Index

---

## Dst Index

World Data Center for Geomagnetism, Kyoto

https://wdc.kugi.kyoto-u.ac.jp/

---

# Project Structure

```
TEC_PROJECT/

│
├── downloader/
│   ├── config.py
│   ├── scanner.py
│   ├── workers.py
│   ├── filenames.py
│   ├── logger.py
│   ├── state.py
│   ├── merge_master.py
│   └── main.py
│
├── scripts/
│   ├── extract_tec.py
│   ├── batch_process.py
│   ├── ionex_parser.py
│   └── ...
│
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Statistical_Analysis.ipynb
│   ├── 03_Neural_Network.ipynb
│   ├── 04_Multiple_Linear_Regression.ipynb
│   ├── 05_Final_Figures.ipynb
│   └── 06_Report_Graphs.ipynb
│
├── data/
│   ├── raw/
│   └── processed/
│
├── results/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Pipeline

```
NASA CDDIS
        │
        ▼
Parallel Downloader
        │
        ▼
IONEX Extraction
        │
        ▼
TEC Parser
        │
        ▼
Daily TEC Dataset
        │
        ▼
Merge Solar & Geomagnetic Indices
        │
        ▼
Master Dataset
        │
        ▼
EDA
        │
        ▼
Statistical Analysis
        │
        ▼
Multiple Linear Regression
        │
        ▼
Neural Network Prediction
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<username>/nigeria-ionospheric-tec-analysis.git
```

Enter the project

```bash
cd nigeria-ionospheric-tec-analysis
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Downloading Data

Run the downloader

```bash
python downloader/main.py
```

The downloader

- downloads missing files only
- resumes interrupted downloads
- supports multiple workers
- automatically extracts downloaded archives
- skips previously downloaded files

---

# Processing TEC

Generate daily TEC values

```bash
python scripts/batch_process.py
```

Output

```
data/processed/tec_daily.csv
```

---

# Building the Master Dataset

Download auxiliary datasets

- Sunspot Number
- Solar Flux
- Kp
- Ap
- Dst

Merge

```bash
python downloader/merge_master.py
```

Output

```
master_dataset.csv
```

---

# Exploratory Data Analysis

Notebook

```
01_EDA.ipynb
```

Includes

- Time series
- Monthly variability
- Seasonal behaviour
- Correlation heatmaps
- Distribution plots

---

# Statistical Analysis

Notebook

```
02_Statistical_Analysis.ipynb
```

Methods

- Pearson Correlation
- Spearman Correlation
- One-way ANOVA
- Seasonal ANOVA

---

# Multiple Linear Regression

Notebook

```
04_Multiple_Linear_Regression.ipynb
```

Includes

- Regression coefficients
- Model summary
- Residual analysis
- VIF
- Diagnostic plots

---

# Neural Network Model

Notebook

```
03_Neural_Network.ipynb
```

Architecture

```
Input

↓

Dense(64)

↓

Dense(32)

↓

Dense(16)

↓

Dense(8)

↓

Output
```

Features

- SSN
- Kp
- Ap
- F10.7
- Dst
- Seasonal sine encoding
- Seasonal cosine encoding

Training

- StandardScaler
- Adam Optimizer
- EarlyStopping
- Validation Split

Performance

| Metric | Value |
|---------|------:|
| MAE | **3.19 TECU** |
| RMSE | **4.36 TECU** |
| R² | **0.811** |

---

# Results

The study found

- Strong positive relationship between TEC and solar activity.
- Moderate influence of geomagnetic activity.
- Clear seasonal variation in TEC.
- Neural Networks significantly outperformed classical regression.

---

# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SciPy
- Statsmodels
- Scikit-learn
- TensorFlow / Keras
- Jupyter Notebook

---

# Requirements

Python

```
>=3.12
```

Major packages

- tensorflow
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- statsmodels
- scikit-learn
- requests

---

# Notes

Large datasets are intentionally excluded from this repository.

Raw IONEX files can be downloaded directly from NASA CDDIS using the provided downloader.

NASA Earthdata credentials are required to access CDDIS products.

---

# License

This project is intended for academic and research purposes.

---

# Citation

If you use this repository in academic work, please cite:

```
Muhammed Adediran

Nigeria Ionospheric Total Electron Content (TEC) Analysis and Prediction Using
Solar and Geomagnetic Indices (2025)
```

---

# Acknowledgements

- NASA CDDIS
- International GNSS Service (IGS)
- SILSO
- NOAA Space Weather Prediction Center
- World Data Center for Geomagnetism, Kyoto

---

## Author

**Muhammed Adediran**

Computer Science | Blockchain Developer | Data Science | Machine Learning

GitHub

https://github.com/admuad
