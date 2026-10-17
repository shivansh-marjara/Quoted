"""Number Guard: a hallucinated fee must not survive."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api"))

from guard import guard_message, stub_message  # noqa: E402


def main() -> int:
    quote = {
        "hours_p10": 12,
        "hours_p50": 19,
        "hours_p90": 24,
        "buffer_hours": 5,
        "hourly_rate": 2000,
        "recommended_fee": 38000,
        "overrun_p50": 1.6,
    }
    ok, passed, illegal = guard_message(
        "I can do this for 9000 in 19 hours.",
        quote,
    )
    assert passed is False
    assert illegal == "9000"
    assert ok == stub_message(quote)
    clean, passed2, illegal2 = guard_message(
        "I can do this in about 19 hours. It might take from 12 to 24. Please pay 38000. I am keeping 5 extra hours in case it runs long.",
        quote,
    )
    assert passed2 is True
    assert illegal2 is None
    assert "19" in clean
    stub = stub_message(quote)
    assert "9000" not in stub
    assert "19" in stub
    assert "38,000" in stub or "38000" in stub
    guarded, stub_ok, stub_illegal = guard_message(stub, quote)
    assert stub_ok is True
    assert stub_illegal is None
    assert guarded == stub
    print("guard ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
