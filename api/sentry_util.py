from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration


def init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=1.0,
        send_default_pii=False,
        integrations=[FastApiIntegration()],
    )


@contextmanager
def gen_ai_span(name: str, model: str | None, op: str = "gen_ai.invoke") -> Iterator[Any]:
    if not os.environ.get("SENTRY_DSN", "").strip():
        yield None
        return
    with sentry_sdk.start_span(op=op, name=name) as span:
        if model:
            span.set_data("gen_ai.request.model", model)
        yield span


def record_usage(span: Any, usage: dict[str, Any] | None) -> None:
    if span is None or not usage:
        return
    if usage.get("input_tokens") is not None:
        span.set_data("gen_ai.usage.input_tokens", usage["input_tokens"])
    if usage.get("output_tokens") is not None:
        span.set_data("gen_ai.usage.output_tokens", usage["output_tokens"])
    if usage.get("model"):
        span.set_data("gen_ai.request.model", usage["model"])
