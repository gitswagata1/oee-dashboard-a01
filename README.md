<div align="center">

# OEE & Loss-Attribution Dashboard — Cell A01

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

Production-grade interactive dashboard computing **OEE (Availability x Performance x Quality)**, TEEP, Six Big Losses breakdown, and per-machine drill-downs from SCADA/MES historian exports.

</div>

<!-- 📸 Add a screenshot: run the app, take a screenshot, save as docs/screenshot.png, then uncomment:
![Dashboard Screenshot](docs/screenshot.png)
-->

> **176 machines · 12,549 records · 51 calendar days (May–Jun 2026)**

## What is OEE?

**Overall Equipment Effectiveness** is the gold standard for measuring manufacturing productivity. It combines three factors:

| Component | Formula | Measures |
|:----------|:--------|:---------|
| **Availability** | Run Time / Planned Time | Downtime losses |
| **Performance** | Ideal Time / Run Time | Speed losses |
| **Quality** | Good Parts / Total Parts | Defect losses |
| **OEE** | A x P x Q | Overall effectiveness |

World-class OEE is **85%+**. This dashboard recomputes all metrics from raw times/counts (vendor columns discarded) using the **Nakajima / SEMI-E10** standard — time-weighted, components capped at 100%.

## Dashboard Features

- **KPI header** — OEE, Availability, Performance, Quality (FPY), TEEP, utilization
- **OEE trend** — daily time-series with selectable A/P/Q overlays
- **Loss Pareto** — horizontal bar chart ranking availability, performance, and quality losses
- **Heatmap** — OEE by hour-of-day x shift for spotting time-based patterns
- **Band distribution** — machine count by OEE band (critical / poor / mid / good)
- **Machine table** — sortable, searchable, with progress bars and CSV export
- **Machine drill-down** — per-machine daily trend + loss breakdown
- **Reconciliation check** — verifies Planned = Run + Availability Loss (audit trail)
- **Data quality panel** — flags, error counts, and sample rows

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Format

The dashboard expects `rows_clean.csv` with one row per **machine x shift x part-run**:

| Column | Description |
|:-------|:------------|
| `date` | Production date |
| `shift` | Shift identifier (A, B, C) |
| `machine` | Machine code |
| `mtype` | Machine type / line |
| `planned` | Planned production time (min) |
| `run` | Actual run time (min) |
| `ideal` | Ideal production time (min) |
| `total` | Total parts produced |
| `ok` | First-pass good parts |
| `valid` | 1 = include in metrics, 0 = excluded |

`meta.json` contains period metadata, methodology notes, and data quality flags.

## Deploy

Push to GitHub, then point [Streamlit Community Cloud](https://share.streamlit.io) at `app.py` on the default branch.

## Tech Stack

- **Streamlit** — interactive web UI with sidebar filters
- **Plotly** — trend charts, heatmaps, Pareto bars, drill-down visualizations
- **Pandas / NumPy** — time-weighted aggregation, data wrangling
- **OEE standard** — Nakajima / SEMI-E10 with overlap correction
