import "./style.css";
import { getHealth, getSample, postImport, postQuote, type QuoteResponse, type Sample } from "./api";

type JobRow = {
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

const HEADER =
  "id,kind,pages_or_screens,integrations,revision_rounds,deadline_days,client_repeat,quoted_hours,actual_hours,quoted_fee,actual_fee,title";

function inr(n: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);
}

function parseJobs(csv: string): JobRow[] {
  const lines = csv.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const head = lines[0].split(",");
  const idx = (k: string) => head.indexOf(k);
  return lines.slice(1).map((line, i) => {
    const cols = line.split(",");
    const n = (k: string, d = 0) => {
      const v = Number(cols[idx(k)]);
      return Number.isFinite(v) ? v : d;
    };
    return {
      id: cols[idx("id")] || String(i + 1),
      kind: cols[idx("kind")] || "other",
      pages_or_screens: n("pages_or_screens", 4),
      integrations: n("integrations", 0),
      revision_rounds: n("revision_rounds", 1),
      deadline_days: n("deadline_days", 14),
      client_repeat: n("client_repeat", 0),
      quoted_hours: n("quoted_hours"),
      actual_hours: n("actual_hours"),
      quoted_fee: n("quoted_fee"),
      actual_fee: n("actual_fee"),
      title: cols.slice(Math.max(idx("title"), 0)).join(",") || "",
    };
  });
}

function toCsv(jobs: JobRow[]): string {
  const rows = jobs.map((j) =>
    [
      j.id,
      j.kind,
      j.pages_or_screens,
      j.integrations,
      j.revision_rounds,
      j.deadline_days,
      j.client_repeat,
      j.quoted_hours,
      j.actual_hours,
      j.quoted_fee,
      j.actual_fee,
      j.title.replace(/,/g, " "),
    ].join(","),
  );
  return [HEADER, ...rows].join("\n");
}

function givenAway(jobs: JobRow[]): { hours: number; money: number } {
  let hours = 0;
  let money = 0;
  for (const j of jobs) {
    const extra = Math.max(0, j.actual_hours - j.quoted_hours);
    hours += extra;
    const rate = j.actual_hours > 0 ? j.actual_fee / j.actual_hours : 0;
    money += extra * rate;
  }
  return { hours: Math.round(hours), money: Math.round(money) };
}

function featureDump(row: QuoteResponse["feature_row"]): string {
  const kinds: Record<string, string> = {
    landing: "a small website",
    store: "an online shop",
    dashboard: "a control panel",
    mobile: "a phone app",
    api: "a behind-the-scenes hookup",
    brand: "a logo / look",
    other: "something else",
  };
  return [
    `I read this as ${kinds[row.kind] || row.kind}.`,
    `${row.pages_or_screens} pages or screens.`,
    `${row.integrations} extra tools to hook up.`,
    `They may ask for changes ${row.revision_rounds} time(s).`,
    `They want it in ${row.deadline_days} days.`,
    row.client_repeat ? "You have worked with them before." : "This is a new client.",
  ].join("\n");
}

const app = document.querySelector<HTMLDivElement>("#app")!;

app.innerHTML = `
  <header class="mast">
    <div>
      <div class="brand">
        <span class="mark">Quoted</span>
      </div>
      <h1>You said 10. It took 19.</h1>
      <p class="lede">You are a freelancer. They said the job was small. You said yes. You promised 10 hours. It took 19. You got paid for 10. The other hours were free. That hurts. Every freelancer has felt this.</p>
      <p class="for">I'm Quoted. I keep those hours so you don't give them away twice. New freelancer or ten years in — this is for you.</p>
    </div>
    <div class="status" id="status"></div>
  </header>
  <p class="whose" id="whose"></p>
  <div class="desk">
    <aside class="carbon" aria-label="Finished jobs">
      <h2>Jobs you already finished</h2>
      <p class="gift" id="gift">—</p>
      <form class="log" id="log">
        <p class="hint">Three finished jobs is enough.</p>
        <label>What did they ask you to do
          <input name="title" required maxlength="80" placeholder="Dentist website" />
        </label>
        <label>What kind of work
          <select name="kind">
            <option value="landing">Small website</option>
            <option value="store">Online shop</option>
            <option value="dashboard">Control panel</option>
            <option value="mobile">Phone app</option>
            <option value="other">Something else</option>
          </select>
        </label>
        <div class="log-hours">
          <label>Hours you promised
            <input name="quoted_hours" type="number" min="1" step="1" required placeholder="12" />
          </label>
          <label>Hours it took you
            <input name="actual_hours" type="number" min="1" step="1" required placeholder="19" />
          </label>
          <label>They paid (optional)
            <input name="actual_fee" type="number" min="0" step="500" placeholder="₹" />
          </label>
        </div>
        <button class="go" type="submit">I finished this job</button>
      </form>
      <div class="job-list" id="job-list" hidden>
        <table class="jobs">
          <thead>
            <tr>
              <th>Job</th>
              <th class="num">You said</th>
              <th class="num">It took</th>
              <th class="num">Gave away</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="jobs"></tbody>
          <tfoot>
            <tr>
              <th colspan="3">Unpaid</th>
              <td class="num over" id="jobs-unpaid">0</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </aside>
    <section class="pad" aria-label="Unpaid hours">
      <div class="pad-head">
        <div>
          <span class="mark pad-brand">Quoted</span>
          <strong id="pad-title">Unpaid</strong>
        </div>
        <span id="predictor"></span>
      </div>
      <div class="perforation" aria-hidden="true"></div>
      <div class="amount">
        <span class="label" id="amount-label">Hours you gave away</span>
        <span class="fig" id="amount">—</span>
      </div>
      <dl class="lines" id="money-line" hidden>
        <div class="line"><dt id="gift-money-label">If you had billed those hours</dt><dd id="gift-money">—</dd></div>
      </dl>
      <dl class="lines next-lines" id="next-lines" hidden>
        <div class="line"><dt>Hours it will take you next</dt><dd id="p50">—</dd></div>
        <div class="line"><dt>Could be as little / as much</dt><dd id="band">—</dd></div>
        <div class="line"><dt>Hours to keep for yourself</dt><dd id="buffer">—</dd></div>
      </dl>
      <p class="message" id="message">That's time you worked and didn't bill.</p>
      <p class="guard" id="guard" hidden></p>
      <pre class="features" id="features" hidden></pre>
    </section>
    <section class="brief-col">
      <h2>They just asked you for something</h2>
      <p class="hint">Paste what they sent. I'll look at how long jobs like this actually took you.</p>
      <textarea id="brief" maxlength="8000" placeholder="A dentist wants a small website by Friday. Four pages. Two rounds of changes. I have not worked with them before."></textarea>
      <button class="go" id="go" type="button">What should I promise this time?</button>
      <div class="actions">
        <button class="quiet" id="blank" type="button">These are my jobs</button>
      </div>
      <details class="file">
        <summary>Or try a message they might send</summary>
        <div class="samples" id="samples"></div>
      </details>
      <details class="file">
        <summary>I have a list of old jobs</summary>
        <p class="hint">Excel, a photo of your notebook, PDF, Word, or CSV.</p>
        <label>Choose a file<input id="csv" type="file" /></label>
      </details>
      <details class="file">
        <summary>See how it looks with an example</summary>
        <p class="hint">Someone else's jobs. Don't copy the prices.</p>
        <button class="quiet" id="borrow" type="button">Show me an example notebook</button>
      </details>
      <p class="err" id="err" hidden></p>
    </section>
  </div>
  <div class="story" id="story" hidden></div>
  <footer class="foot">
    <span class="mark foot-brand">Quoted</span>
    <p>For freelancers who said 10 and it took 19.</p>
  </footer>
`;

let jobs: JobRow[] = [];
let whose: "borrowed" | "yours" = "yours";
let sample: Sample | null = null;

const STORE = "quoted-notebook";

function persist() {
  try {
    localStorage.setItem(STORE, JSON.stringify({ whose, jobs }));
  } catch {
    /* private mode */
  }
}

function restore(): { whose: "borrowed" | "yours"; jobs: JobRow[] } | null {
  try {
    const raw = localStorage.getItem(STORE);
    if (!raw) return null;
    const o = JSON.parse(raw) as { whose?: string; jobs?: JobRow[] };
    if (o.whose !== "borrowed" && o.whose !== "yours") return null;
    if (!Array.isArray(o.jobs)) return null;
    return { whose: o.whose, jobs: o.jobs };
  } catch {
    return null;
  }
}

function lateHours(j: JobRow): number {
  return Math.max(0, Math.round(j.actual_hours - j.quoted_hours));
}

function storyJob(): JobRow | null {
  if (whose !== "yours" || jobs.length === 0) return null;
  return jobs[0];
}

function paintStory() {
  const el = document.querySelector("#story") as HTMLElement;
  const j = storyJob();
  if (!j) {
    el.hidden = true;
    el.innerHTML = "";
    return;
  }
  const extra = lateHours(j);
  const title = escapeHtml(j.title || "that job");
  el.hidden = false;
  el.innerHTML =
    extra > 0
      ? `<ol>
          <li><strong>They asked for ${title}.</strong> You said yes. That's how the work came in.</li>
          <li><strong>You quoted ${j.quoted_hours} hours.</strong> They said yes. You started.</li>
          <li><strong>It took ${j.actual_hours}.</strong> You invoiced ${j.quoted_hours}. That's +${extra} hours unpaid. Next time they ask, I stop you.</li>
        </ol>`
      : `<ol>
          <li><strong>They asked for ${title}.</strong> You said yes.</li>
          <li><strong>You quoted ${j.quoted_hours} hours.</strong></li>
          <li><strong>It took ${j.actual_hours}.</strong> You billed what you worked. Write the next one too.</li>
        </ol>`;
}

function renderJobs() {
  hideErr();
  persist();
  const body = document.querySelector("#jobs")!;
  const list = document.querySelector("#job-list") as HTMLElement;
  list.hidden = jobs.length === 0;
  const gift = givenAway(jobs);
  document.querySelector("#gift")!.textContent =
    jobs.length === 0 ? "No unpaid hours yet." : `${gift.hours} hours unpaid`;
  document.querySelector("#amount")!.textContent = jobs.length === 0 ? "0" : String(gift.hours);
  document.querySelector("#amount-label")!.textContent = "Hours you gave away";
  document.querySelector("#pad-title")!.textContent = "Unpaid";
  const moneyLabel = document.querySelector("#gift-money-label")!;
  const moneyVal = document.querySelector("#gift-money")!;
  if (jobs.length === 0) {
    moneyLabel.textContent = "If you had billed those hours";
    moneyVal.textContent = "—";
  } else if (whose === "borrowed") {
    moneyLabel.textContent = "These hours are not yours";
    moneyVal.textContent = "A warning, not a bill";
  } else {
    moneyLabel.textContent = "If you had billed those hours";
    moneyVal.textContent = inr(gift.money);
  }
  document.querySelector("#p50")!.textContent = "—";
  document.querySelector("#band")!.textContent = "—";
  document.querySelector("#buffer")!.textContent = "—";
  const features = document.querySelector("#features") as HTMLElement;
  features.textContent = "";
  features.hidden = true;
  (document.querySelector("#next-lines") as HTMLElement).hidden = true;
  (document.querySelector("#guard") as HTMLElement).hidden = true;
  document.querySelector("#predictor")!.textContent = "";
  const moneyLine = document.querySelector("#money-line") as HTMLElement;
  if (jobs.length === 0) {
    moneyLine.hidden = true;
  } else if (whose === "borrowed") {
    moneyLine.hidden = false;
  } else {
    moneyLine.hidden = gift.money <= 0;
  }
  const bar = document.querySelector("#whose") as HTMLElement;
  bar.classList.toggle("yours", whose !== "borrowed");
  bar.textContent =
    whose === "borrowed"
      ? "These aren't your jobs. They're an example. Add your own — new or ten years in."
      : jobs.length === 0
        ? "Your notebook. Add a job you already finished."
        : jobs.length < 3
          ? `Your notebook. ${jobs.length} job${jobs.length === 1 ? "" : "s"} so far. I need 3 to talk about the next promise.`
          : "Your notebook. These hours are yours.";
  document.querySelector("#message")!.textContent =
    jobs.length === 0
      ? "Write a job you already finished, or import a list. This is yours from the first one."
      : whose === "borrowed"
        ? "Example hours. Don't copy the prices. Copy the lesson, then add your own jobs."
        : "That's you. Time you worked and didn't bill.";
  body.innerHTML = jobs
    .map((j) => {
      const extra = lateHours(j);
      return `<tr data-id="${escapeHtml(j.id)}" data-kind="${escapeHtml(j.kind)}">
        <td>${escapeHtml(j.title || j.kind)}</td>
        <td class="num">${j.quoted_hours}</td>
        <td class="num">${j.actual_hours}</td>
        <td class="over">${extra ? `+${extra}` : "—"}</td>
        <td><button class="forget" type="button" data-forget="${escapeHtml(j.id)}">Forget</button></td>
      </tr>`;
    })
    .join("");
  const unpaid = document.querySelector("#jobs-unpaid");
  if (unpaid) unpaid.textContent = String(gift.hours);
  body.querySelectorAll("[data-forget]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = (btn as HTMLElement).getAttribute("data-forget");
      jobs = jobs.filter((j) => j.id !== id);
      if (jobs.length === 0) whose = "yours";
      renderJobs();
    });
  });
  paintStory();
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
}

function paintNext(q: QuoteResponse) {
  document.querySelector("#pad-title")!.textContent = "Next time";
  document.querySelector("#amount-label")!.textContent = "Do not promise less than";
  document.querySelector("#amount")!.textContent = inr(q.quote.recommended_fee);
  (document.querySelector("#next-lines") as HTMLElement).hidden = false;
  document.querySelector("#p50")!.textContent = String(q.quote.hours_p50);
  document.querySelector("#band")!.textContent = `${q.quote.hours_p10} to ${q.quote.hours_p90}`;
  document.querySelector("#buffer")!.textContent = `${q.quote.buffer_hours} hours`;
  document.querySelector("#message")!.textContent =
    whose === "borrowed"
      ? `${q.message} I'm looking at other freelancers' jobs, not yours.`
      : q.message;
  const features = document.querySelector("#features") as HTMLElement;
  features.hidden = false;
  features.textContent = featureDump(q.feature_row);
  document.querySelector("#predictor")!.textContent =
    whose === "borrowed"
      ? `I looked at ${q.quote.n_jobs} other freelancers`
      : `I looked at ${q.quote.n_jobs} of your jobs`;
  const bar = document.querySelector("#whose") as HTMLElement;
  bar.textContent =
    whose === "borrowed"
      ? "I looked at the example. The pad is my answer — not a bill."
      : "I looked at your jobs. The pad is my answer.";
  document.querySelectorAll("#jobs tr").forEach((tr) => {
    const likeThis = tr.getAttribute("data-kind") === q.feature_row.kind;
    tr.classList.toggle("used", likeThis);
  });
  const g = document.querySelector("#guard") as HTMLElement;
  if (q.guard_passed) {
    g.hidden = true;
    g.textContent = "";
    g.classList.remove("fail");
  } else {
    g.hidden = false;
    g.classList.add("fail");
    g.textContent = "I rewrote the message. A number in it wasn't from your jobs.";
  }
}

async function runNext() {
  const brief = (document.querySelector("#brief") as HTMLTextAreaElement).value.trim();
  const err = document.querySelector("#err") as HTMLElement;
  const go = document.querySelector("#go") as HTMLButtonElement;
  err.hidden = true;
  if (jobs.length < 3) {
    err.hidden = false;
    err.textContent = "I need 3 jobs you already finished. Type them or import a file.";
    return;
  }
  if (brief.length < 8) {
    err.hidden = false;
    err.textContent = "Paste what they sent you.";
    return;
  }
  go.disabled = true;
  go.textContent = "Looking at jobs like yours…";
  try {
    const q = await postQuote({ brief, history_csv: toCsv(jobs) });
    paintNext(q);
  } catch (e) {
    err.hidden = false;
    err.textContent = e instanceof Error ? e.message : "Could not look at the notebook.";
  } finally {
    go.disabled = false;
    go.textContent = "What should I promise this time?";
  }
}

async function boot() {
  const status = document.querySelector("#status")!;
  try {
    const h = await getHealth();
    status.textContent = h.ok ? "" : "Cannot reach the server.";
  } catch {
    status.textContent = "Cannot reach Quoted right now.";
  }
  try {
    sample = await getSample();
    const saved = restore();
    if (saved && saved.jobs.length > 0) {
      whose = saved.whose;
      jobs = saved.jobs;
    } else {
      jobs = [];
      whose = "yours";
    }
    renderJobs();
    const box = document.querySelector("#samples")!;
    box.innerHTML = "";
    for (const b of sample.briefs) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = b.label;
      btn.addEventListener("click", () => {
        (document.querySelector("#brief") as HTMLTextAreaElement).value = b.brief;
      });
      box.appendChild(btn);
    }
  } catch {
    const errEl = document.querySelector("#err") as HTMLElement;
    errEl.hidden = false;
    errEl.textContent = "Could not load Quoted.";
    renderJobs();
  }
}

document.querySelector("#go")!.addEventListener("click", () => void runNext());
document.querySelector("#borrow")!.addEventListener("click", () => {
  if (!sample) return;
  jobs = parseJobs(sample.history_csv);
  whose = "borrowed";
  renderJobs();
});
document.querySelector("#blank")!.addEventListener("click", () => {
  jobs = [];
  whose = "yours";
  renderJobs();
});
document.querySelector("#log")!.addEventListener("submit", (ev) => {
  ev.preventDefault();
  const f = ev.target as HTMLFormElement;
  const data = new FormData(f);
  const quoted = Number(data.get("quoted_hours"));
  const actual = Number(data.get("actual_hours"));
  const rawFee = String(data.get("actual_fee") || "").trim();
  const fee = rawFee ? Number(rawFee) : 0;
  if (whose === "borrowed") {
    jobs = [];
    whose = "yours";
  }
  jobs.unshift({
    id: `${Date.now()}-${jobs.length + 1}`,
    kind: String(data.get("kind") || "other"),
    pages_or_screens: 4,
    integrations: 0,
    revision_rounds: 1,
    deadline_days: 14,
    client_repeat: 0,
    quoted_hours: quoted,
    actual_hours: actual,
    quoted_fee: fee,
    actual_fee: fee,
    title: String(data.get("title") || "Job"),
  });
  f.reset();
  renderJobs();
  const title = f.querySelector("input[name='title']") as HTMLInputElement | null;
  title?.focus();
});
function showErr(text: string) {
  const err = document.querySelector("#err") as HTMLElement;
  err.hidden = false;
  err.textContent = text;
}

function hideErr() {
  const err = document.querySelector("#err") as HTMLElement;
  err.hidden = true;
  err.textContent = "";
}

document.querySelector("#csv")!.addEventListener("change", async (ev) => {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  hideErr();
  const goLabel = document.querySelector("#go") as HTMLButtonElement;
  const prev = goLabel.textContent;
  try {
    goLabel.disabled = true;
    goLabel.textContent = "Reading your file…";
    const imported = await postImport(file);
    jobs = imported.jobs.map((j) => ({
      id: j.id,
      kind: j.kind,
      pages_or_screens: j.pages_or_screens,
      integrations: j.integrations,
      revision_rounds: j.revision_rounds,
      deadline_days: j.deadline_days,
      client_repeat: j.client_repeat,
      quoted_hours: j.quoted_hours,
      actual_hours: j.actual_hours,
      quoted_fee: j.quoted_fee,
      actual_fee: j.actual_fee,
      title: j.title,
    }));
    whose = "yours";
    renderJobs();
  } catch (e) {
    showErr(e instanceof Error ? e.message : "We could not read that file. Type the jobs on the left.");
  } finally {
    goLabel.disabled = false;
    goLabel.textContent = prev;
    input.value = "";
  }
});

void boot();
