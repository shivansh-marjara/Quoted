# Glossary

Terms for Quoted. No implementation details.

## Job

A finished piece of work. It has `quoted_hours`, `actual_hours`, `quoted_fee`, `actual_fee`, and tags (`kind`, `pages_or_screens`, `integrations`, `revision_rounds`, `deadline_days`, `client_repeat`).

## History

The table of Jobs. Type them, or drop Excel, a photo, a PDF, Word, JSON, or CSV. Three rows is enough to run; forty is better.

## Brief

The new client request, as plain text.

## Feature Row

The structured record Gemma is allowed to emit from a Brief: `kind`, `pages_or_screens`, `integrations`, `revision_rounds`, `deadline_days`, `client_repeat`. Not hours. Not rupees.

## Quote

`hours_p10`, `hours_p50`, `hours_p90`, `recommended_fee`, `buffer_hours`. The only numbers that may appear in the written message.

## Overrun

`actual_hours / quoted_hours` on a Job. This is what the product is really predicting.

## Number Guard

If the written Quote contains a digit sequence that is not in the TabPFN output, the write-up is rejected and regenerated once; if it fails again, the stub shows the raw numbers with no prose.

## Client

The person who asked for the work. Not "customer."
