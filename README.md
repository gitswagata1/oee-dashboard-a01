# OEE & Loss-Attribution Dashboard — Cell A01

Interactive Streamlit dashboard computing OEE (Availability × Performance × Quality),
TEEP, the Six-Big-Losses split, and per-machine breakdowns from a SCADA/historian export
(01 May – 21 Jun 2026, 176 machines, 12,549 records).

Numbers mirror the standalone HTML dashboard exactly: metrics are **recomputed** from raw
counts/times (vendor A/P/Q/OEE columns discarded), **time-weighted**, and **capped at 100%**.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` — the dashboard
- `rows_clean.csv` — cleaned row-level records (one row per machine × shift × part-run)
- `meta.json` — data-quality flags + period metadata
- `.streamlit/config.toml` — light theme
- `requirements.txt` — streamlit, pandas, numpy, plotly

## Deploy (Streamlit Community Cloud)
Push this folder to a GitHub repo, then at share.streamlit.io point a new app at
`app.py` on the default branch.
