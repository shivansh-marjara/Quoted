from __future__ import annotations

import csv
import io
import json
import os
import re
import zipfile
from typing import Any

from history import KINDS, Job

KIND_WORDS = (
    ("landing", ("landing", "website", "one-pager", "one pager", "webpage")),
    ("store", ("shopify", "store", "shop", "ecommerce", "e-commerce")),
    ("dashboard", ("dashboard", "admin", "erp", "panel")),
    ("mobile", ("android", "ios", "app", "mobile")),
    ("api", ("api", "webhook", "bot")),
    ("brand", ("logo", "brand", "identity")),
)

ALIASES = {
    "quoted_hours": (
        "quoted_hours",
        "quotedhours",
        "promised",
        "promised_hours",
        "hourspromised",
        "hours_promised",
        "yousaid",
        "you_said",
        "said",
        "hoursyoupromised",
        "promisedhours",
        "estimate",
        "estimated_hours",
        "quoted",
    ),
    "actual_hours": (
        "actual_hours",
        "actualhours",
        "actual",
        "took",
        "it_took",
        "ittook",
        "hoursittook",
        "real_hours",
        "hours_taken",
        "spent",
        "hours_spent",
    ),
    "quoted_fee": (
        "quoted_fee",
        "quotedfee",
        "quoted_price",
        "price_quoted",
        "asked",
    ),
    "actual_fee": (
        "actual_fee",
        "actualfee",
        "paid",
        "fee",
        "price",
        "charged",
        "amount",
        "rupees",
        "inr",
        "money",
    ),
    "title": ("title", "job", "name", "project", "client", "work", "description"),
    "kind": ("kind", "type", "category"),
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _header_map(headers: list[str]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for h in headers:
        n = _norm(h)
        for field, aliases in ALIASES.items():
            if n in {_norm(a) for a in aliases} and field not in mapped.values():
                mapped[h] = field
                break
    return mapped


def _kind(text: str) -> str:
    t = (text or "").lower()
    for kind, words in KIND_WORDS:
        if any(w in t for w in words):
            return kind
    return "other" if t not in KINDS else t


def _num(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if v != v:  # NaN
            return None
        return float(v)
    s = str(v).strip().replace(",", "")
    s = re.sub(r"[₹$]", "", s)
    if not s:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    return float(m.group(0))


def jobs_from_dicts(rows: list[dict[str, Any]]) -> list[Job]:
    if not rows:
        return []
    headers = list(rows[0].keys())
    mapping = _header_map([str(h) for h in headers])
    jobs: list[Job] = []
    for i, raw in enumerate(rows, start=1):
        rec: dict[str, Any] = {}
        for k, v in raw.items():
            field = mapping.get(str(k))
            if field:
                rec[field] = v
        title = str(rec.get("title") or raw.get("title") or f"Job {i}")
        kind_src = rec.get("kind") or title
        qh = _num(rec.get("quoted_hours"))
        ah = _num(rec.get("actual_hours"))
        if qh is None or ah is None or qh <= 0 or ah <= 0:
            continue
        qf = _num(rec.get("quoted_fee")) or 0.0
        af = _num(rec.get("actual_fee")) or 0.0
        try:
            jobs.append(
                Job(
                    id=str(i),
                    kind=_kind(str(kind_src)),
                    pages_or_screens=4,
                    integrations=0,
                    revision_rounds=1,
                    deadline_days=14,
                    client_repeat=0,
                    quoted_hours=qh,
                    actual_hours=ah,
                    quoted_fee=max(0.0, qf),
                    actual_fee=max(0.0, af),
                    title=title[:80],
                )
            )
        except Exception:
            continue
    return jobs


_NOTE_LINE = re.compile(
    r"(?P<title>.*?)(?:I\s+)?(?:said|promised)\s+(?P<q>\d+(?:\.\d+)?)\s*(?:hours?)?"
    r"[,.\s]+(?:it\s+)?took\s+(?P<a>\d+(?:\.\d+)?)(?:\s*hours?)?"
    r"(?:.*?paid\s+(?P<fee>\d[\d,]*))?",
    re.I,
)


def _from_notes_rules(text: str) -> list[Job]:
    rows: list[dict[str, Any]] = []
    for raw in re.split(r"[\n\r]+|(?<=\d)\.\s+", text):
        line = re.sub(r"\s+", " ", raw).strip(" -•\t")
        if not line:
            continue
        m = _NOTE_LINE.search(line)
        if not m:
            continue
        title = re.sub(r"^(?:finished jobs|jobs)\s*", "", m.group("title"), flags=re.I)
        title = title.strip(" .,:;-") or f"Job {len(rows) + 1}"
        fee = (m.group("fee") or "0").replace(",", "")
        rows.append(
            {
                "title": title[:80],
                "quoted_hours": m.group("q"),
                "actual_hours": m.group("a"),
                "actual_fee": fee,
            }
        )
    return jobs_from_dicts(rows)


def _from_table_text(text: str) -> list[Job]:
    sample = text.lstrip("\ufeff")
    try:
        dialect = csv.Sniffer().sniff(sample[:4000], delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(sample), dialect=dialect)
    rows = [{k: v for k, v in (row or {}).items() if k} for row in reader]
    return jobs_from_dicts(rows)


def _from_excel(data: bytes) -> list[Job]:
    import pandas as pd

    df = pd.read_excel(io.BytesIO(data), engine=None)
    df = df.dropna(how="all")
    rows = df.astype(object).where(df.notna(), None).to_dict(orient="records")
    return jobs_from_dicts(rows)


def _from_json(data: bytes) -> list[Job]:
    obj = json.loads(data.decode("utf-8-sig"))
    if isinstance(obj, dict):
        for v in obj.values():
            if isinstance(v, list):
                obj = v
                break
        else:
            obj = [obj]
    if not isinstance(obj, list):
        raise ValueError("JSON was not a list of jobs.")
    return jobs_from_dicts([x for x in obj if isinstance(x, dict)])


def _from_docx(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    return re.sub(r"<[^>]+>", " ", xml)


LLM_PROMPT = """These are finished freelance jobs.
Return ONLY a JSON array. Each item:
{"title":"short name","kind":"landing|store|dashboard|mobile|api|brand|other","quoted_hours":number,"actual_hours":number,"quoted_fee":number,"actual_fee":number}
quoted_hours = hours they promised. actual_hours = hours it really took.
If a fee is missing use 0. Skip rows you cannot read. No markdown."""


def _parse_jobs_json(text: str) -> list[Job]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < 0:
        raise ValueError("no json array")
    return jobs_from_dicts(json.loads(text[start : end + 1]))


def _llm_jobs_from_text(text: str) -> list[Job]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Could not read that file. Add the jobs by hand, or import a spreadsheet."
        )
    from google import genai

    model_name = os.environ.get("GEMMA_MODEL", "gemma-3-12b-it").strip()
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=model_name,
        contents=LLM_PROMPT + "\n\n" + text[:12000],
    )
    return _parse_jobs_json(resp.text or "")


def _llm_jobs_from_bytes(data: bytes, mime: str) -> list[Job]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Could not read that photo or PDF. Add the jobs by hand."
        )
    from google import genai
    from google.genai import types

    model_name = os.environ.get("GEMMA_MODEL", "gemma-3-12b-it").strip()
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=data, mime_type=mime),
            LLM_PROMPT,
        ],
    )
    return _parse_jobs_json(resp.text or "")


def sniff(name: str, mime: str, data: bytes) -> str:
    n = (name or "").lower()
    m = (mime or "").lower()
    if n.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".bmp", ".tif", ".tiff")):
        return "image"
    if n.endswith(".pdf") or m == "application/pdf" or data[:4] == b"%PDF":
        return "pdf"
    if n.endswith(".docx") or (data[:2] == b"PK" and b"word/" in data[:12000]):
        return "docx"
    if n.endswith((".xlsx", ".xlsm", ".xls")) or "spreadsheet" in m:
        return "excel"
    if n.endswith(".json") or m.endswith("json"):
        return "json"
    if n.endswith((".csv", ".tsv", ".txt")):
        return "table"
    if data[:8] == b"\x89PNG\r\n\x1a\n" or data[:3] == b"\xff\xd8\xff":
        return "image"
    if data[:2] == b"PK":
        return "excel"
    return "text"


def import_bytes(name: str, mime: str, data: bytes) -> tuple[list[Job], str]:
    kind = sniff(name, mime, data)
    if kind == "excel":
        try:
            return _from_excel(data), "excel"
        except Exception:
            if data[:2] == b"PK":
                try:
                    return _llm_jobs_from_text(_from_docx(data)), "word"
                except Exception:
                    pass
            raise ValueError("Could not read that spreadsheet. Add the jobs by hand.")
    if kind == "json":
        return _from_json(data), "json"
    if kind == "table":
        text = data.decode("utf-8-sig", errors="replace")
        jobs = _from_table_text(text)
        if jobs:
            return jobs, "table"
        jobs = _from_notes_rules(text)
        if jobs:
            return jobs, "notes"
        return _llm_jobs_from_text(text), "notes"
    if kind == "docx":
        text = _from_docx(data)
        jobs = _from_notes_rules(text)
        if jobs:
            return jobs, "word"
        return _llm_jobs_from_text(text), "word"
    if kind in ("image", "pdf"):
        mime_use = mime if mime and mime != "application/octet-stream" else (
            "application/pdf" if kind == "pdf" else "image/jpeg"
        )
        return _llm_jobs_from_bytes(data, mime_use), kind
    text = data.decode("utf-8-sig", errors="replace")
    jobs = _from_table_text(text)
    if jobs:
        return jobs, "table"
    jobs = _from_notes_rules(text)
    if jobs:
        return jobs, "notes"
    return _llm_jobs_from_text(text), "notes"
