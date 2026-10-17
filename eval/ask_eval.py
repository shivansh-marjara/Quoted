"""Twenty Briefs → Feature Row schema check. No hours, no rupees in the JSON."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

from extract import extract_with_gemma  # noqa: E402
from history import KINDS  # noqa: E402

BRIEFS = [
    "Landing page for a dentist in Pune. Four sections, WhatsApp button, two revision rounds. Live by Friday, five days. New client.",
    "Shopify store for a sari shop I already built a logo for last year. Twelve collection pages, Razorpay and Shiprocket, one revision, three weeks.",
    "Admin dashboard for a coaching class. Attendance, fees, eight screens, Google Sheets sync, two revisions. First time. Ten days.",
    "Logo and visiting cards, four options, three revision rounds, ten days, new restaurant.",
    "Android app for delivery boys, eight screens, one maps integration, two revisions, a month, new client.",
    "Razorpay webhooks into their existing ERP, four endpoints, one revision, two weeks, they hired me last year.",
    "One-pager for a plumber I already work with. Three sections, no integrations, no extra revisions, two weeks.",
    "Inventory dashboard, ten screens, three integrations, two revisions, two weeks, new distributor.",
    "Kids clothes Shopify, nine pages, one payment integration, three revisions, ten days, new.",
    "Email sequence, three mails, one Mailchimp integration, one revision, five days.",
    "School ERP slice, twelve screens, two integrations, three revisions, eight days. First time.",
    "Repeat spices store, six pages, Razorpay, one revision, eighteen days.",
    "GST JSON dump API, five endpoints, three integrations, one revision, twenty days, new.",
    "Interior studio landing, five sections, Instagram shop button, two revisions, six days, new.",
    "Simple habit iOS app, five screens, no backend, one revision, three weeks.",
    "Hostel mess menu dashboard, seven screens, two integrations, two revisions, twelve days, new.",
    "Real estate one-pager, seven sections, WhatsApp and maps, two revisions, nine days, new.",
    "Repeat banner for an event, one screen, no integrations, no revisions, two days.",
    "Fleet tracking dashboard, nine screens, three integrations, two revisions, sixteen days, new.",
    "Restaurant menu design, eight items illustrated, four revision rounds, seven days, new.",
]


def main() -> int:
    ok = 0
    leaked = 0
    for i, brief in enumerate(BRIEFS, 1):
        row, source, _ = extract_with_gemma(brief)
        dump = row.model_dump()
        valid = (
            dump["kind"] in KINDS
            and dump["pages_or_screens"] >= 1
            and dump["integrations"] >= 0
            and dump["revision_rounds"] >= 0
            and dump["deadline_days"] >= 1
            and dump["client_repeat"] in (0, 1)
        )
        # Feature Row must not carry hours/fees — schema enforces this.
        extra = set(dump) - {
            "kind",
            "pages_or_screens",
            "integrations",
            "revision_rounds",
            "deadline_days",
            "client_repeat",
        }
        if extra:
            leaked += 1
        if valid and not extra:
            ok += 1
        print(f"{i:02d} {source:14s} valid={valid} {dump}")
    print(f"\n{ok}/{len(BRIEFS)} valid Feature Rows, {leaked} leaked extra keys.")
    return 0 if ok == len(BRIEFS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
