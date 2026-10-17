"""Leak-free effort backtest on Desharnais (77 complete cases).

Train on earlier YearEnd folds, test on the next year.
Baselines: training-set mean, ordinary least squares, k-NN analogy.
TabPFN-3.5 runs when TABPFN_TOKEN is set.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

CSV = Path(__file__).resolve().parent / "desharnais.csv"
FEATURES = ["TeamExp", "ManagerExp", "Length", "Transactions", "Entities", "PointsAjust", "Language"]
INCOMPLETE = {38, 44, 66, 75}


def load() -> np.ndarray:
    import csv

    rows = []
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = int(row["Project"])
            if pid in INCOMPLETE:
                continue
            if int(row["TeamExp"]) < 0 or int(row["ManagerExp"]) < 0:
                continue
            rec = [float(row[c]) for c in FEATURES]
            rec.append(float(row["YearEnd"]))
            rec.append(float(row["Effort"]))
            rows.append(rec)
    return np.array(rows, dtype=float)


def mae(y, p):
    return float(np.mean(np.abs(y - p)))


def mdae(y, p):
    return float(np.median(np.abs(y - p)))


def pred25(y, p):
    return float(np.mean(np.abs(y - p) / np.maximum(y, 1e-6) < 0.25))


def analog_predict(Xtr, ytr, Xte, k=3):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd[sd == 0] = 1.0
    Ztr = (Xtr - mu) / sd
    Zte = (Xte - mu) / sd
    preds = []
    kk = max(1, min(k, len(Xtr)))
    for z in Zte:
        d = np.sqrt(((Ztr - z) ** 2).sum(axis=1))
        idx = np.argsort(d)[:kk]
        preds.append(float(np.median(ytr[idx])))
    return np.array(preds)


def linreg_predict(Xtr, ytr, Xte):
    from sklearn.linear_model import LinearRegression

    m = LinearRegression()
    m.fit(Xtr, ytr)
    return m.predict(Xte)


def tabpfn_predict(Xtr, ytr, Xte):
    from tabpfn_client import TabPFNRegressor, set_access_token

    token = os.environ.get("TABPFN_TOKEN", "").strip()
    if not token:
        raise RuntimeError("no TABPFN_TOKEN")
    set_access_token(token)
    model = TabPFNRegressor.create_default_for_version("v3.5")
    model.fit(Xtr, ytr)
    return np.ravel(model.predict(Xte)).astype(float)


def metrics(y, p, name):
    return {
        "name": name,
        "MAE": round(mae(y, p), 1),
        "MdAE": round(mdae(y, p), 1),
        "PRED25": round(pred25(y, p), 3),
        "n": int(len(y)),
    }


def main() -> int:
    data = load()
    years = sorted(set(data[:, -2].astype(int)))
    y_all = []
    preds = {"mean": [], "linear": [], "analog": [], "tabpfn": []}
    tabpfn_ok = bool(os.environ.get("TABPFN_TOKEN", "").strip())
    fold_notes = []

    for year in years:
        train = data[data[:, -2] < year]
        test = data[data[:, -2] == year]
        if len(train) < 15 or len(test) < 3:
            continue
        Xtr, ytr = train[:, :-2], train[:, -1]
        Xte, yte = test[:, :-2], test[:, -1]
        p_mean = np.full(len(yte), ytr.mean())
        p_lin = linreg_predict(Xtr, ytr, Xte)
        p_ana = analog_predict(Xtr, ytr, Xte)
        y_all.append(yte)
        preds["mean"].append(p_mean)
        preds["linear"].append(p_lin)
        preds["analog"].append(p_ana)
        fold_notes.append(
            f"Year 19{year}: train {len(train)}, test {len(test)}, "
            f"mean MAE {mae(yte, p_mean):.0f}, linear MAE {mae(yte, p_lin):.0f}, "
            f"analog MAE {mae(yte, p_ana):.0f}"
        )
        if tabpfn_ok:
            try:
                p_t = tabpfn_predict(Xtr, ytr, Xte)
                preds["tabpfn"].append(p_t)
                fold_notes[-1] += f", TabPFN MAE {mae(yte, p_t):.0f}"
            except Exception as e:
                tabpfn_ok = False
                fold_notes[-1] += f", TabPFN failed ({e})"

    y = np.concatenate(y_all)
    rows = []
    for name in ("mean", "linear", "analog"):
        p = np.concatenate(preds[name])
        rows.append(metrics(y, p, name))
    tabpfn_row = None
    if preds["tabpfn"] and len(preds["tabpfn"]) == len(preds["mean"]):
        p = np.concatenate(preds["tabpfn"])
        tabpfn_row = metrics(y, p, "tabpfn-3.5")
        rows.append(tabpfn_row)

    # Where analog/linear beat mean on this data is expected; TabPFN may lose
    # on a tiny yearly fold. Report the worst fold for honesty if we have TabPFN.

    lines = [
        "# Desharnais backtest",
        "",
        "Dataset: PROMISE Desharnais software cost estimation, 81 projects.",
        "Dropped 4 incomplete projects (38, 44, 66, 75) as in Shepperd & Schofield 1997, leaving 77 cases.",
        "Split: rolling origin by `YearEnd`. Train on earlier years, test on the next year.",
        "Folds with fewer than 15 train or 3 test rows are skipped.",
        "Target: `Effort` (person-hours). Features: TeamExp, ManagerExp, Length, Transactions, Entities, PointsAjust, Language.",
        "",
        "PRED(25) is the fraction of predictions within 25% of actual effort, the usual number in this literature.",
        "",
        "## Results",
        "",
        "| Model | MAE (hours) | MdAE (hours) | PRED(25) | n |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        lines.append(f"| {r['name']} | {r['MAE']} | {r['MdAE']} | {r['PRED25']} | {r['n']} |")
    lines += ["", "## Folds", ""]
    for n in fold_notes:
        lines.append(f"- {n}")
    lines += [
        "",
        "## How to read this",
        "",
        "The mean baseline quotes the same hours for every project. Linear regression is what a careful freelancer with a spreadsheet would do.",
        "Analog is 3-nearest-neighbour on standardized features, the method Shepperd used on this same table.",
        "",
    ]
    if tabpfn_row is None:
        lines.append(
            "TabPFN-3.5 was not run in this file. Set `TABPFN_TOKEN` and rerun `python eval/backtest.py`."
        )
    else:
        # find who won MAE
        best = min(rows, key=lambda r: r["MAE"])
        worst = max(rows, key=lambda r: r["MAE"])
        lines.append(
            f"Lowest MAE on this split: **{best['name']}** ({best['MAE']}). "
            f"Highest MAE: **{worst['name']}** ({worst['MAE']})."
        )
        t = tabpfn_row
        mean_row = next(r for r in rows if r["name"] == "mean")
        lin_row = next(r for r in rows if r["name"] == "linear")
        if t["MAE"] > lin_row["MAE"]:
            lines.append(
                f"TabPFN lost to linear regression on MAE ({t['MAE']} vs {lin_row['MAE']}). "
                "That is reported rather than hidden. The product still uses TabPFN because "
                "the freelancer History is 20–40 rows of mixed kinds, not 77 rows of function points, "
                "and because we need a quantile band (p10–p90), which the linear fit does not give."
            )
        elif t["MAE"] > mean_row["MAE"]:
            lines.append(
                f"TabPFN lost to the mean baseline on MAE ({t['MAE']} vs {mean_row['MAE']}). "
                "That is a real miss on this split and is left in the table."
            )
        else:
            lines.append(
                f"TabPFN beat the mean baseline on MAE ({t['MAE']} vs {mean_row['MAE']}) "
                f"and posted PRED(25)={t['PRED25']}."
            )
    lines += [
        "",
        "## Source",
        "",
        "Original: J. M. Desharnais, Universite de Montreal, 1989. PROMISE ARFF via Martin Shepperd.",
        "File vendored at `eval/desharnais.csv`.",
        "",
    ]
    report = ROOT / "eval" / "REPORT.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
