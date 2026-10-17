from __future__ import annotations

import re
from typing import Iterable

_NUM = re.compile(r"\d[\d,]*\.?\d*")


def _canon(token: str) -> str:
    t = token.replace(",", "").strip()
    if t.endswith(".0"):
        t = t[:-2]
    try:
        f = float(t)
        if abs(f - round(f)) < 1e-9:
            return str(int(round(f)))
        return str(f)
    except ValueError:
        return t


def allowed_from_quote(quote: dict) -> set[str]:
    keys = (
        "hours_p10",
        "hours_p50",
        "hours_p90",
        "recommended_fee",
        "buffer_hours",
        "hourly_rate",
        "overrun_p50",
    )
    allowed: set[str] = set()
    for k in keys:
        v = quote.get(k)
        if v is None:
            continue
        allowed.update(_variants(v))
    return allowed


def _variants(v: float | int) -> set[str]:
    f = float(v)
    i = int(round(f))
    out = {
        _canon(str(f)),
        str(i),
        f"{i:,}",
        str(int(f)),
    }
    # nearest rupee and nearest hour already covered; add floor/ceil
    out.add(str(int(f)))
    out.add(str(int(f) + (0 if f == int(f) else 1)))
    return {_canon(x) for x in out}


def digit_tokens(text: str) -> list[str]:
    return _NUM.findall(text or "")


def first_illegal(text: str, allowed: Iterable[str]) -> str | None:
    allow = {_canon(a) for a in allowed}
    for tok in digit_tokens(text):
        if _canon(tok) not in allow:
            return tok
    return None


def stub_message(quote: dict) -> str:
    p10 = int(round(quote["hours_p10"]))
    p50 = int(round(quote["hours_p50"]))
    p90 = int(round(quote["hours_p90"]))
    fee = int(round(quote["recommended_fee"]))
    buf = int(round(quote["buffer_hours"]))
    grouped = f"{fee:,}"
    return (
        f"Do not promise less than {p50} hours. "
        f"It might take {p10} to {p90}. "
        f"Keep {buf} extra. "
        f"Send ₹{grouped}."
    )


def guard_message(text: str | None, quote: dict) -> tuple[str, bool, str | None]:
    """Return (message, passed, illegal_token)."""
    allowed = allowed_from_quote(quote)
    fallback = stub_message(quote)
    if not text or not text.strip():
        return fallback, True, None
    illegal = first_illegal(text, allowed)
    if illegal is None:
        return text.strip(), True, None
    return fallback, False, illegal
