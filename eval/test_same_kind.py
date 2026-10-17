"""A small website must follow the clinic, not the shop."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

from extract import correct_kind, _rule_based  # noqa: E402
from history import FeatureRow, Job  # noqa: E402
from quote import analog_quantiles, build_quote  # noqa: E402

PHYSIO = (
    "A physiotherapist in Pune wants a small website by Friday. "
    "Five pages, WhatsApp, two rounds of changes. First time working with them."
)


def job(kind: str, hours: float, title: str) -> Job:
    return Job(
        id=title,
        kind=kind,
        pages_or_screens=5,
        integrations=1,
        revision_rounds=2,
        deadline_days=7,
        client_repeat=0,
        quoted_hours=hours * 0.7,
        actual_hours=hours,
        quoted_fee=0,
        actual_fee=0,
        title=title,
    )


def main() -> int:
    assert correct_kind(PHYSIO, "api") == "landing"
    row = _rule_based(PHYSIO)
    assert row.kind == "landing", row.kind
    jobs = [
        job("landing", 16, "Clinic website"),
        job("store", 48, "Sari shop"),
        job("dashboard", 40, "Coaching dashboard"),
    ]
    p10, p50, p90, source = analog_quantiles(jobs, row)
    assert source == "analog"
    assert p50 == 16, p50
    q = build_quote(jobs, row)
    assert q["hours_p50"] == 16, q
    assert q["predictor"] in ("analog", "analog_fallback")
    print("physio follows clinic:", q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
