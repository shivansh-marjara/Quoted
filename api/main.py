from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")

from extract import extract_with_gemma, write_prose_with_gemma  # noqa: E402
from import_file import import_bytes  # noqa: E402
from guard import allowed_from_quote, guard_message  # noqa: E402
from history import FeatureRow, Job, jobs_from_json, parse_history_csv  # noqa: E402
from quote import build_quote  # noqa: E402
from sentry_util import gen_ai_span, init_sentry, record_usage  # noqa: E402

init_sentry()

app = FastAPI(title="Quoted", version="1.0.0")

origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_HISTORY = (ROOT / "samples" / "history.csv").read_text(encoding="utf-8")
SAMPLE_BRIEFS = [
    {
        "id": "dentist",
        "label": "Dentist website by Friday",
        "brief": (
            "Landing page for a dentist in Pune. Four sections, WhatsApp button, "
            "two revision rounds. They want it live by Friday, so five days. New client."
        ),
    },
    {
        "id": "physio",
        "label": "Physio website by Friday",
        "brief": (
            "A physiotherapist in Pune wants a small website by Friday. "
            "Five pages, WhatsApp, two rounds of changes. First time working with them."
        ),
    },
    {
        "id": "sari",
        "label": "Sari shop, three weeks",
        "brief": (
            "Shopify store for a sari shop I already built a logo for last year. "
            "About twelve collection pages, Razorpay and Shiprocket, one revision round, three weeks."
        ),
    },
    {
        "id": "coaching",
        "label": "Coaching dashboard in 10 days",
        "brief": (
            "Admin dashboard for a coaching class. Attendance, fees, eight screens, "
            "Google Sheets sync, two revision rounds. First time with them. "
            "They asked yesterday and need it in ten days."
        ),
    },
]


class ExtractIn(BaseModel):
    brief: str = Field(min_length=8, max_length=8000)


class QuoteIn(BaseModel):
    brief: str | None = Field(default=None, max_length=8000)
    history_csv: str | None = None
    history: list[dict] | None = None
    feature_row: dict | None = None


def _load_jobs(body: QuoteIn) -> list[Job]:
    if body.history_csv and body.history_csv.strip():
        jobs = parse_history_csv(body.history_csv)
    elif body.history:
        jobs = jobs_from_json(body.history)
    else:
        jobs = parse_history_csv(SAMPLE_HISTORY)
    if len(jobs) < 3:
        raise HTTPException(400, "Add 3 finished jobs first.")
    return jobs


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "tabpfn": bool(os.environ.get("TABPFN_TOKEN", "").strip()),
        "gemma": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
        "sentry": bool(os.environ.get("SENTRY_DSN", "").strip()),
    }


@app.get("/api/sample")
def sample():
    return {"history_csv": SAMPLE_HISTORY, "briefs": SAMPLE_BRIEFS}


@app.post("/api/import")
async def import_jobs(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(400, "That file was empty.")
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(400, "That file is larger than 8 MB.")
    try:
        jobs, source = import_bytes(file.filename or "upload", file.content_type or "", data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception:
        raise HTTPException(
            400,
            "Could not read that file. Add the jobs by hand.",
        )
    if not jobs:
        raise HTTPException(
            400,
            "No jobs in that file. Add hours promised and hours it took, or enter them by hand.",
        )
    return {
        "source": source,
        "n": len(jobs),
        "jobs": [j.model_dump() for j in jobs],
    }


@app.post("/api/extract")
def extract(body: ExtractIn):
    with gen_ai_span("gemma extract", os.environ.get("GEMMA_MODEL")) as span:
        row, source, usage = extract_with_gemma(body.brief)
        record_usage(span, usage)
    return {
        "feature_row": row.model_dump(),
        "source": source,
        "usage": usage,
    }


@app.post("/api/quote")
def quote(body: QuoteIn):
    jobs = _load_jobs(body)
    extract_meta: dict | None = None
    if body.feature_row:
        row = FeatureRow.model_validate(body.feature_row)
        source = "provided"
    else:
        if not body.brief or len(body.brief.strip()) < 8:
            raise HTTPException(400, "Pass a Brief or a Feature Row.")
        with gen_ai_span("gemma extract", os.environ.get("GEMMA_MODEL")) as span:
            row, source, usage = extract_with_gemma(body.brief)
            record_usage(span, usage)
        extract_meta = {"source": source, "usage": usage}

    with gen_ai_span("tabpfn quote", "tabpfn-3.5", op="gen_ai.predict") as span:
        try:
            q = build_quote(jobs, row)
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
        if span is not None:
            span.set_data("quoted.predictor", q["predictor"])
            span.set_data("quoted.n_jobs", q["n_jobs"])
            span.set_data("quoted.hours_p50", q["hours_p50"])

    allowed = sorted(allowed_from_quote(q), key=len)
    prose = None
    prose_usage = None
    if body.brief:
        with gen_ai_span("gemma message", os.environ.get("GEMMA_MODEL")) as span:
            prose, prose_usage = write_prose_with_gemma(q, body.brief, allowed)
            record_usage(span, prose_usage)
    message, passed, illegal = guard_message(prose, q)
    return {
        "feature_row": row.model_dump(),
        "extract_source": source if not body.feature_row else "provided",
        "extract": extract_meta,
        "quote": q,
        "message": message,
        "guard_passed": passed,
        "guard_illegal": illegal,
        "prose_usage": prose_usage,
    }


STATIC = Path(__file__).resolve().parent / "static"
if STATIC.exists():
    app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404)
        file = STATIC / path
        if path and file.is_file():
            return FileResponse(file)
        return FileResponse(STATIC / "index.html")
