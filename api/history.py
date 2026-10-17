from __future__ import annotations

import csv
import io
from typing import Any

from pydantic import BaseModel, Field, field_validator

KINDS = ("landing", "store", "dashboard", "mobile", "api", "brand", "other")
KIND_INDEX = {k: i for i, k in enumerate(KINDS)}

FEATURE_KEYS = (
    "kind",
    "pages_or_screens",
    "integrations",
    "revision_rounds",
    "deadline_days",
    "client_repeat",
)


class FeatureRow(BaseModel):
    kind: str
    pages_or_screens: int = Field(ge=1, le=200)
    integrations: int = Field(ge=0, le=50)
    revision_rounds: int = Field(ge=0, le=20)
    deadline_days: int = Field(ge=1, le=365)
    client_repeat: int = Field(ge=0, le=1)

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in KIND_INDEX:
            return "other"
        return v


class Job(FeatureRow):
    id: str = "0"
    quoted_hours: float = Field(gt=0)
    actual_hours: float = Field(gt=0)
    quoted_fee: float = Field(ge=0)
    actual_fee: float = Field(ge=0)
    title: str = ""


def parse_history_csv(text: str) -> list[Job]:
    reader = csv.DictReader(io.StringIO(text))
    jobs: list[Job] = []
    for i, row in enumerate(reader, start=1):
        if not row or not any((v or "").strip() for v in row.values()):
            continue
        jobs.append(
            Job(
                id=str(row.get("id") or i),
                kind=row.get("kind") or "other",
                pages_or_screens=int(float(row["pages_or_screens"])),
                integrations=int(float(row["integrations"])),
                revision_rounds=int(float(row["revision_rounds"])),
                deadline_days=int(float(row["deadline_days"])),
                client_repeat=int(float(row["client_repeat"])),
                quoted_hours=float(row["quoted_hours"]),
                actual_hours=float(row["actual_hours"]),
                quoted_fee=float(row["quoted_fee"]),
                actual_fee=float(row["actual_fee"]),
                title=str(row.get("title") or ""),
            )
        )
    return jobs


def jobs_from_json(rows: list[dict[str, Any]]) -> list[Job]:
    return [Job.model_validate(r) for r in rows]


def feature_vector(row: FeatureRow) -> list[float]:
    return [
        float(KIND_INDEX.get(row.kind, KIND_INDEX["other"])),
        float(row.pages_or_screens),
        float(row.integrations),
        float(row.revision_rounds),
        float(row.deadline_days),
        float(row.client_repeat),
    ]


def median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2.0


def realized_hourly_rates(jobs: list[Job]) -> list[float]:
    rates = []
    for j in jobs:
        if j.actual_hours > 0 and j.actual_fee > 0:
            rates.append(j.actual_fee / j.actual_hours)
    return rates
