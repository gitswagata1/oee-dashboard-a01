"""Validation and metadata for user-uploaded production CSV files."""

from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "date", "shift", "machine", "mtype", "hour",
    "planned", "run", "ideal", "aloss", "ploss", "qloss",
    "total", "ok", "valid",
}
NUMERIC_COLUMNS = {
    "hour", "planned", "run", "ideal", "aloss", "ploss", "qloss",
    "total", "ok", "valid",
}


def load_uploaded_data(source) -> pd.DataFrame:
    """Read an uploaded CSV and reject data that would break OEE calculations."""
    try:
        df = pd.read_csv(source)
    except (pd.errors.ParserError, UnicodeError, ValueError, OSError) as exc:
        raise ValueError("Cannot read CSV. Please upload a valid CSV file.") from exc

    df.columns = df.columns.str.strip()
    if df.columns.has_duplicates:
        raise ValueError("CSV contains duplicate column names.")

    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    if df.empty:
        raise ValueError("CSV has no data rows.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Column 'date' contains empty or invalid dates.")

    for col in ("shift", "machine", "mtype"):
        if df[col].isna().any() or df[col].astype(str).str.strip().eq("").any():
            raise ValueError(f"Column '{col}' contains empty values.")
        df[col] = df[col].astype(str).str.strip()

    for col in sorted(NUMERIC_COLUMNS):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if not np.isfinite(df[col].to_numpy(dtype=float)).all():
            raise ValueError(f"Column '{col}' contains missing or invalid numbers.")
        if (df[col] < 0).any():
            raise ValueError(f"Column '{col}' cannot contain negative numbers.")

    for col in ("hour", "total", "ok", "valid"):
        if (df[col] % 1 != 0).any():
            raise ValueError(f"Column '{col}' must contain whole numbers.")
        df[col] = df[col].astype(int)

    if not df["hour"].between(0, 23).all():
        raise ValueError("Column 'hour' must be between 0 and 23.")
    if not df["valid"].isin([0, 1]).all():
        raise ValueError("Column 'valid' must contain only 0 or 1.")
    if (df["ok"] > df["total"]).any():
        raise ValueError("Column 'ok' cannot exceed 'total'.")
    if not df["valid"].eq(1).any():
        raise ValueError("CSV contains no rows marked valid (valid = 1).")

    return df


def uploaded_metadata(df: pd.DataFrame) -> dict:
    """Use the uploaded dataset's own period and counts, not sample metadata."""
    start = df["date"].min().date()
    end = df["date"].max().date()
    return {
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "period_days": (end - start).days + 1,
        "connected": df["machine"].nunique(),
        "n_raw": len(df),
        "n_kept_valid": int(df["valid"].eq(1).sum()),
        "shift_min_threshold": 1,
        "method": {"world_class": 85, "typical": 60},
    }
