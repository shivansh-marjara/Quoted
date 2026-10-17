from __future__ import annotations

import os
from typing import Any

import numpy as np

from history import (
    FeatureRow,
    Job,
    feature_vector,
    median,
    realized_hourly_rates,
)


def _round_hours(x: float) -> float:
    x = max(1.0, float(x))
    return float(int(round(x)))


def _round_fee(x: float) -> float:
    x = max(0.0, float(x))
    # nearest 500 rupees, typical for Indian freelance quotes
    return float(int(round(x / 500.0) * 500))


def analog_quantiles(jobs: list[Job], row: FeatureRow, k: int = 5) -> tuple[float, float, float, str]:
    """k-NN on standardized Feature Rows. Prefer the same kind of job. Used when TabPFN is unavailable."""
    same = [j for j in jobs if j.kind == row.kind]
    pool = same if same else jobs
    if len(pool) == 1:
        y = float(pool[0].actual_hours)
        return max(1.0, y * 0.85), y, y * 1.3, "analog"
    X = np.array([feature_vector(j) for j in pool], dtype=float)
    y = np.array([j.actual_hours for j in pool], dtype=float)
    q = np.array(feature_vector(row), dtype=float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    Zn = (X - mu) / sd
    zq = (q - mu) / sd
    dist = np.sqrt(((Zn - zq) ** 2).sum(axis=1))
    k = max(1, min(k, len(pool)))
    idx = np.argsort(dist)[:k]
    sample = y[idx]
    p10, p50, p90 = np.quantile(sample, [0.1, 0.5, 0.9])
    if p90 < p50:
        p90 = p50
    if p10 > p50:
        p10 = p50
    return float(p10), float(p50), float(p90), "analog"


def tabpfn_quantiles(jobs: list[Job], row: FeatureRow) -> tuple[float, float, float, str]:
    token = os.environ.get("TABPFN_TOKEN", "").strip()
    same = [j for j in jobs if j.kind == row.kind]
    pool = same if same else jobs
    # One clinic and a shop is not a table of clinics. TabPFN needs enough
    # rows of the same kind; otherwise analog uses the clinic, not the shop.
    if not token or len(pool) < 3:
        return analog_quantiles(jobs, row)

    try:
        from tabpfn_client import TabPFNRegressor, set_access_token

        set_access_token(token)
        X = np.array([feature_vector(j) for j in pool], dtype=float)
        y = np.array([j.actual_hours for j in pool], dtype=float)
        x_new = np.array([feature_vector(row)], dtype=float)
        model = TabPFNRegressor.create_default_for_version("v3.5")
        model.fit(X, y)
        q = model.predict(x_new, output_type="quantiles", quantiles=[0.1, 0.5, 0.9])
        # q shape: (3, n) or (n, 3) depending on client version
        arr = np.array(q, dtype=float)
        if arr.ndim == 2 and arr.shape[0] == 3:
            p10, p50, p90 = float(arr[0, 0]), float(arr[1, 0]), float(arr[2, 0])
        elif arr.ndim == 2 and arr.shape[1] == 3:
            p10, p50, p90 = float(arr[0, 0]), float(arr[0, 1]), float(arr[0, 2])
        else:
            p50 = float(np.ravel(arr)[0])
            p10, p90 = p50 * 0.75, p50 * 1.4
        if p90 < p50:
            p90 = p50
        if p10 > p50:
            p10 = p50
        return p10, p50, p90, "tabpfn"
    except Exception:
        p10, p50, p90, _ = analog_quantiles(jobs, row)
        return p10, p50, p90, "analog_fallback"


def build_quote(jobs: list[Job], row: FeatureRow) -> dict[str, Any]:
    if len(jobs) < 3:
        raise ValueError("Add 3 finished jobs first.")
    p10, p50, p90, source = tabpfn_quantiles(jobs, row)
    p10 = _round_hours(p10)
    p50 = _round_hours(p50)
    p90 = _round_hours(max(p90, p50))
    rates = realized_hourly_rates(jobs)
    hourly = _round_fee(median(rates) if rates else 2000.0)
    if hourly <= 0:
        hourly = 2000.0
    fee = _round_fee(p50 * hourly)
    buffer_hours = _round_hours(max(0.0, p90 - p50))
    quoted_med = median([j.quoted_hours for j in jobs])
    overrun_p50 = round(p50 / quoted_med, 2) if quoted_med else 1.0
    return {
        "hours_p10": p10,
        "hours_p50": p50,
        "hours_p90": p90,
        "buffer_hours": buffer_hours,
        "hourly_rate": hourly,
        "recommended_fee": fee,
        "overrun_p50": overrun_p50,
        "predictor": source,
        "n_jobs": len(jobs),
    }
