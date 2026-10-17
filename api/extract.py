from __future__ import annotations

import json
import os
import re
from typing import Any

from history import FeatureRow

EXTRACT_SCHEMA = {
    "kind": "one of: landing, store, dashboard, mobile, api, brand, other",
    "pages_or_screens": "integer >= 1",
    "integrations": "integer >= 0 (Razorpay, Shiprocket, Sheets, WhatsApp API, etc.)",
    "revision_rounds": "integer >= 0",
    "deadline_days": "integer >= 1",
    "client_repeat": "1 if they have worked with this client before, else 0",
}

SYSTEM = """You extract a Feature Row from a freelancer Brief.
Emit ONLY a JSON object with these keys and nothing else:
kind, pages_or_screens, integrations, revision_rounds, deadline_days, client_repeat.

Rules:
- kind must be one of: landing, store, dashboard, mobile, api, brand, other
- Do not invent hours.
- Do not invent rupees, dollars, or any fee.
- Do not include any key other than the six above.
- If a field is missing, pick the smallest plausible integer (1 page, 0 integrations, 1 revision, 14 days, 0 repeat).
"""


_WORDS = {
    "twenty": "20",
    "eighteen": "18",
    "sixteen": "16",
    "fifteen": "15",
    "fourteen": "14",
    "thirteen": "13",
    "twelve": "12",
    "eleven": "11",
    "thirty": "30",
    "three": "3",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "four": "4",
    "five": "5",
    "six": "6",
    "ten": "10",
    "two": "2",
    "one": "1",
}


def _digits(text: str) -> str:
    t = text.lower()
    t = t.replace("one-pager", "landing")
    t = t.replace("one pager", "landing")
    t = re.sub(r"\ba month\b", "30 days", t)
    t = re.sub(r"\bno extra revisions?\b", "0 revisions", t)
    t = re.sub(r"\bno revisions?\b", "0 revisions", t)
    for w, n in _WORDS.items():
        t = re.sub(rf"\b{w}\b", n, t)
    return t


def _rule_based(brief: str) -> FeatureRow:
    t = _digits(brief)
    kind = "other"
    if any(w in t for w in ("shopify", "store", "sku", "catalogue", "catalog", "ecommerce", "e-commerce")):
        kind = "store"
    elif any(w in t for w in ("dashboard", "admin", "erp", "attendance", "inventory")):
        kind = "dashboard"
    elif any(w in t for w in ("android", "ios", "mobile app", "app for")):
        kind = "mobile"
    elif any(w in t for w in ("webhook", "api", "razorpay", "sheets to", "bot")):
        kind = "api"
    elif any(w in t for w in ("logo", "brand", "visiting card", "menu design")):
        kind = "brand"
    elif any(w in t for w in ("landing", "one-pager", "one pager", "webpage", "website")):
        kind = "landing"

    def near(patterns: list[str], default: int) -> int:
        for p in patterns:
            m = re.search(p, t)
            if m:
                return int(m.group(1))
        return default

    pages = near(
        [
            r"(\d+)\s*(?:sections?|pages?|screens?|collection)",
            r"(?:sections?|pages?|screens?)\s*[:=]?\s*(\d+)",
        ],
        4 if kind == "landing" else 6,
    )
    integrations = 0
    for name in ("razorpay", "shiprocket", "sheets", "whatsapp", "gst", "erp", "webhook"):
        if name in t:
            integrations += 1
    revisions = near(
        [
            r"(\d+)\s*revision",
            r"revision rounds?\s*[:=]?\s*(\d+)",
        ],
        1,
    )
    days = near([r"(\d+)\s*days?"], 14)
    weeks = re.search(r"(\d+)\s*weeks?", t)
    if weeks:
        days = int(weeks.group(1)) * 7
    if "friday" in t and days == 14:
        days = 5
    repeat = 1 if any(w in t for w in ("last year", "repeat", "already built", "existing client", "again")) else 0
    if any(w in t for w in ("new client", "first time")):
        repeat = 0
    return FeatureRow(
        kind=kind,
        pages_or_screens=max(1, pages),
        integrations=max(0, integrations),
        revision_rounds=max(0, revisions),
        deadline_days=max(1, days),
        client_repeat=repeat,
    )


def _parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no json object")
    return json.loads(text[start : end + 1])


def _from_model_dict(d: dict[str, Any]) -> FeatureRow:
    return FeatureRow(
        kind=str(d.get("kind") or "other"),
        pages_or_screens=int(d.get("pages_or_screens") or 1),
        integrations=int(d.get("integrations") or 0),
        revision_rounds=int(d.get("revision_rounds") or 0),
        deadline_days=int(d.get("deadline_days") or 14),
        client_repeat=int(d.get("client_repeat") or 0),
    )


def extract_with_gemma(brief: str) -> tuple[FeatureRow, str, dict[str, Any]]:
    """Returns Feature Row, source, usage dict."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model_name = os.environ.get("GEMMA_MODEL", "gemma-3-12b-it").strip()
    if not api_key:
        row = _rule_based(brief)
        return row, "rule", {"input_tokens": 0, "output_tokens": 0, "model": None}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = SYSTEM + "\n\nBrief:\n" + brief
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=256,
            ),
        )
        text = (resp.text or "").strip()
        usage = {
            "input_tokens": getattr(getattr(resp, "usage_metadata", None), "prompt_token_count", 0) or 0,
            "output_tokens": getattr(getattr(resp, "usage_metadata", None), "candidates_token_count", 0) or 0,
            "model": model_name,
        }
        row = _from_model_dict(_parse_json_object(text))
        return row, "gemma", usage
    except Exception:
        row = _rule_based(brief)
        return row, "rule_fallback", {"input_tokens": 0, "output_tokens": 0, "model": model_name}


def write_prose_with_gemma(quote: dict, brief: str, allowed_numbers: list[str]) -> tuple[str | None, dict[str, Any]]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model_name = os.environ.get("GEMMA_MODEL", "gemma-3-12b-it").strip()
    if not api_key:
        return None, {"input_tokens": 0, "output_tokens": 0, "model": None}
    numbers = ", ".join(allowed_numbers)
    prompt = f"""Write 2 short sentences a freelancer would send on WhatsApp.
You may ONLY use these numbers, and no others: {numbers}
Do not write "please pay". Do not add dates, page counts, or extra figures.
Brief (for tone only, ignore any numbers in it): {brief[:400]}
Hours they should promise: {quote['hours_p50']}. Band {quote['hours_p10']}-{quote['hours_p90']}. Fee {quote['recommended_fee']}. Extra hours to keep: {quote['buffer_hours']}.
"""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=200),
        )
        usage = {
            "input_tokens": getattr(getattr(resp, "usage_metadata", None), "prompt_token_count", 0) or 0,
            "output_tokens": getattr(getattr(resp, "usage_metadata", None), "candidates_token_count", 0) or 0,
            "model": model_name,
        }
        return (resp.text or "").strip(), usage
    except Exception:
        return None, {"input_tokens": 0, "output_tokens": 0, "model": model_name}
