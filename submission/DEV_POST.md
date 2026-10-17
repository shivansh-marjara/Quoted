*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

# You said 10. It took 19.

You are a freelancer. They said the job was small. You said yes. You promised 10 hours. It took 19. You got paid for 10. The other hours were free. That leftover is the product.

I quoted eight thousand rupees for a landing page. It took nineteen hours. I did not invoice the extra. **Quoted** is a notebook of promised vs actual hours so the next number you send is honest. A chatbot does not get to invent the price.

Someone who has already given a week away would pay Rs 499 a month to stop doing that once. The first under-quote they catch pays for the year. My own first sit-down with the live pad did **not** pay. I say that later, in their words.

## What I Built

Quoted is not a machine that invents a price.

You write jobs you already finished: what they asked, hours you promised, hours it took, money they paid if you remember. You do not need a spreadsheet. Type three jobs from memory, or drop Excel, a photo of a notebook, a PDF, Word, JSON, or CSV.

When someone asks for the next job, you paste what they sent.

Then the split the whole product sits on:

```text
What they asked  →  Gemma reads it     →  six facts. Never hours. Never rupees.
Finished jobs    →  TabPFN-3.5         →  hours as a band
hours × your rate →  the number you send
If the sentence invents a digit, we throw it away
```

Gemma (Google's open-weight model, via AI Studio) may only write: what kind of job, how many pages, extra tools, rounds of changes, how soon, have you worked with them. If it tries to pick a price, `api/guard.py` throws the sentence away and keeps the numbers from the table.

TabPFN-3.5, Prior Labs' tabular foundation model, fits on your small table — the size of a freelancer's year — and predicts hours at 10 / 50 / 90. Code multiplies the middle by what you actually earn per hour, and rounds to five hundred rupees.

New or ten years in: you land on your own empty notebook. Three finished jobs is enough. There is an example notebook if you want to click around first. It is labelled as not yours.

## Demo

Live, no signup: [https://quoted-32zd.onrender.com](https://quoted-32zd.onrender.com)

Repo: [https://github.com/shivansh-marjara/Quoted](https://github.com/shivansh-marjara/Quoted)

Open the pad. You land on your notebook, empty.

**The 90-second click (example notebook):**

1. Open **See how it looks with an example**.
2. Open **Or try a message they might send** → **Dentist website by Friday**.
3. Press **What should I promise this time?**

That click fills as **19 hours** (14 to 22) and **₹28,500**. Keep 3 extra hours. The sentence says: *Do not promise less than 19 hours.*

If the Prior Labs key is set, that click is TabPFN-3.5. Health on the live site is `tabpfn: true`, `gemma: true`. If the key is missing, similar past jobs still fill the stub and the pad says so. I am not going to pretend a key-less demo is TabPFN.

**Your own jobs:** type three finished ones, or drop `samples/upload-test.xlsx`. Paste what they asked this week. Press the same button.

## How I Built It

**The ask.** Six fields. No hours. No fees. Gemma 3 (`gemma-3-12b-it`) when `GEMINI_API_KEY` is set. If the key is missing, a rule reader fills the same six facts so the pad still works. `eval/ask_eval.py` runs twenty asks and checks that the JSON has exactly those keys.

This laptop has 4 GB of RAM. It will not host a 12B model. Gemma runs on AI Studio. That sentence belongs here. Pretending it “runs locally” would be the dishonest version of open.

**The notebook.** Forty sample jobs of an Indian product freelancer, with real overruns: Friday websites blow up, repeat clients do not. You replace them by typing, or by dropping a file. `api/import_file.py` sniffs Excel, photos, PDF, Word, JSON, CSV.

**The hours.** `tabpfn-client`, model `v3.5`. Fit on hours it really took, given those six facts. Predict 0.1, 0.5, 0.9. Fee is the middle hours times the median of (money they paid / hours it took), rounded to 500. If TabPFN is missing, k-NN on the same kind of job fills the stub.

**The sentence.** Any digit in the WhatsApp line must be a rounded form of those hours, the extra hours, the rate, or the fee. Fail once, try again; fail again, drop the prose.

**The backtest.** PROMISE Desharnais, 77 complete software projects, rolling origin by year. Analog MAE 1972 hours, linear 2013, mean 3114, n=46. The table is in `eval/REPORT.md`. TabPFN was empty in that file until the key existed. I left the row empty on purpose rather than fake it.

**Render.** One Docker web service from `render.yaml`. The image builds the pad and serves FastAPI on the same origin. Live health: `GET /api/health`.

The pad looks like a carbon-copy notebook because that is the object this replaces, not a dashboard.

## Why Does Open Innovation Matter?

Closed quote tools want the ask, and they bill per call. After month one you are renting your own memory. A freelancer's history is 20–40 private rows: client names, hours, fees. That table should not be pasted into a closed chat as few-shot text.

TabPFN is a foundation model for tables exactly that size. Fit on my rows, emit a band, no per-quote theatre. You cannot get that from a general chat API without uploading every past client's ask. The open tabular weights (and the hosted 3.5 API on the free tier) are what make this a product instead of a demo.

Gemma's weights are open, so the reader is swappable. Today it is AI Studio because of RAM. The same six-field contract would work on a laptop later. The digit check is only possible because hours come from a model whose output is a short list of numbers. A chatbot quote has no such list.

Where a closed API is worse here: it cannot fit your table, it meters the ask, and you cannot print a before/after against linear regression on Desharnais because you do not own the weights or the fit.

## My Agent Session

I built Quoted in Cursor. No Entire / DevRelay capture to embed. The repo is the session.

## My First User

My freelancer friends were busy. I sat with the live pad myself, as the first user, the way the protocol asked: three finished jobs, one ask from this week, then the three questions. I am not going to invent a friend who said yes.

**What I typed**

| Job | Promised | Took | Unpaid |
| --- | --- | --- | --- |
| Clinic website | 10 | 16 | +6 |
| Sari shop | 36 | 48 | +12 |
| Coaching dashboard | 28 | 40 | +12 |

Unpaid on the pad: **30 hours**. That matched.

Then I pasted: *A physiotherapist in Pune wants a small website by next Friday. Five pages, WhatsApp button, two rounds of changes. I have not worked with them before.*

Quoted said: **Do not promise less than 39 hours. Send ₹58,500.** Band 15–51.

My last small site was 16 hours. 39 is too big. Gemma had read a small website as “a behind-the-scenes hookup,” so TabPFN looked at the shop and the dashboard, not the clinic.

**The three answers, verbatim**

1. **Would you pay Rs 499 a month for this?**  
   No. Not this month. I would keep using it for free. I would pay after it quotes a small website like my clinic, not like my shop.

2. **What did it get wrong?**  
   It called a small website a hookup and told me 39 hours / ₹58,500. My last small site was 16 hours. The wait on first open also felt unfinished.

3. **What do you want it to tell you next?**  
   Which of my jobs it used. “This is like your clinic, not your shop.”

If a freelancer I know sits with it before the deadline, I will replace this with their words. Until then, this is the truth: the idea is payable, this session was not.

## Prize Categories

- Best Use of TabPFN
- Best Use of Gemma
- Best Use of Render
