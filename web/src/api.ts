export type FeatureRow = {
  kind: string;
  pages_or_screens: number;
  integrations: number;
  revision_rounds: number;
  deadline_days: number;
  client_repeat: number;
};

export type QuoteNums = {
  hours_p10: number;
  hours_p50: number;
  hours_p90: number;
  buffer_hours: number;
  hourly_rate: number;
  recommended_fee: number;
  overrun_p50: number;
  predictor: string;
  n_jobs: number;
};

export type QuoteResponse = {
  feature_row: FeatureRow;
  extract_source: string;
  quote: QuoteNums;
  message: string;
  guard_passed: boolean;
  guard_illegal: string | null;
};

export type Sample = {
  history_csv: string;
  briefs: { id: string; label: string; brief: string }[];
};

export type Health = {
  ok: boolean;
  tabpfn: boolean;
  gemma: boolean;
  sentry: boolean;
};

export async function getHealth(): Promise<Health> {
  const r = await fetch("/api/health");
  if (!r.ok) throw new Error("health failed");
  return r.json();
}

export async function getSample(): Promise<Sample> {
  const r = await fetch("/api/sample");
  if (!r.ok) throw new Error("sample failed");
  return r.json();
}

export type ImportedJob = {
  id: string;
  kind: string;
  pages_or_screens: number;
  integrations: number;
  revision_rounds: number;
  deadline_days: number;
  client_repeat: number;
  quoted_hours: number;
  actual_hours: number;
  quoted_fee: number;
  actual_fee: number;
  title: string;
};

export async function postImport(file: File): Promise<{ source: string; n: number; jobs: ImportedJob[] }> {
  const body = new FormData();
  body.append("file", file, file.name);
  const r = await fetch("/api/import", { method: "POST", body });
  if (!r.ok) {
    let detail = r.statusText;
    try {
      const j = await r.json();
      detail = j.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "Could not read that file.");
  }
  return r.json();
}

export async function postQuote(body: {
  brief: string;
  history_csv: string;
}): Promise<QuoteResponse> {
  const r = await fetch("/api/quote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    let detail = r.statusText;
    try {
      const j = await r.json();
      detail = j.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return r.json();
}
