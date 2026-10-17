*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

# You said 10. It took 19.

**If you only read one paragraph:** You always say a job will take 10 hours. It takes 19. You still charge for 10, so you work for free. This is a notebook of jobs you already finished. The red number is hours you gave away. Next time someone asks, we look at that notebook and stop you promising 10 again. A chatbot does not get to invent the price.

I quoted eight thousand rupees for a landing page. It took nineteen hours. I did not invoice the extra. That gap is the product. Someone would pay Rs 499 a month to stop doing that once.

## What I Built

**Quoted** is not a machine that invents a price.

You write finished jobs: hours you promised, hours it really took, money they paid if you remember. You do not need a CSV. Type three jobs from memory, or drop Excel, a photo of a notebook, a PDF, Word, or JSON.

When someone asks for the next job, you paste what they want.

Gemma (Google's open-weight model) is allowed to read the ask and write down six facts: what kind of job, how many pages, extra tools, rounds of changes, how soon, have you worked with them. It is not allowed to pick hours or rupees.

TabPFN-3.5, Prior Labs' tabular foundation model, looks at your small table of finished jobs and predicts hours as a band. Code multiplies the middle of that band by what you actually earn per hour, and rounds to five hundred rupees. If the written message tries a digit that did not come from that prediction, we throw the sentence away and keep the numbers.

Who pays: a freelancer who has already given a week away. Rs 499 a month. The first under-quote they stop pays for the year. The notebook grows, so this is not a one-time licence.

The job TabPFN was built for is a small table. Forty private rows is too few for XGBoost theatre and too sensitive to paste into a closed chat. That is the side hustle.

New or ten years in: you start on your own notebook. Type finished jobs or import a file. Three is enough. If you want to see how it feels first, there is an example notebook — labelled as not yours.

## Demo

Live pad: https://quoted-32zd.onrender.com

Repo: https://github.com/shivansh-marjara/Quoted

Open the pad. You land on your own notebook, empty. Add three jobs, or press **See an example notebook** if you want to click around first.

Click **Dentist website by Friday**. Press **What should I promise this time?**

That click currently fills as **19 hours** (it might take 14 to 22) and **₹28,500**. Keep 3 extra hours. The sentence says: *Do not promise less than 19 hours.*

If the Prior Labs key is set, the same click is TabPFN-3.5. If it is missing, the pad still fills from similar past jobs (the method papers use on a table this small). I am not going to pretend a key-less demo is TabPFN.

You land on your own notebook. Type three jobs, or import a file. **See an example notebook** is optional.

I tried three jobs from memory: one small website, one shop, one control panel. The dentist ask still came back **19 hours** — it looked at the one small website, not the shop.

Optional: drop `samples/upload-test.xlsx` under **I have a list of old jobs**.

## Code

{% github shivansh-marjara/Quoted %}

The split the whole project sits on:

```text
What they asked  →  Gemma reads it  →  six facts, never hours, never rupees
Finished jobs    →  TabPFN-3.5      →  hours as a band
hours × your rate →  the number you send
If the sentence invents a digit, we throw it away
```

Gemma never picks the rupees. If it tries, `api/guard.py` replaces the sentence with the raw numbers.

## How I Built It

**The ask.** Six fields. No hours. No fees. Gemma 3 through Google AI Studio when `GEMINI_API_KEY` is set. If the key is missing, a rule reader fills the same six facts so the pad still works. `eval/ask_eval.py` runs twenty asks and checks that the JSON has exactly those keys.

**The notebook.** Forty sample jobs of an Indian product freelancer, with real overruns: Friday websites blow up, repeat clients do not. You can replace them by typing, or by dropping any file.

**The hours.** `tabpfn-client`, model `v3.5`. Fit on hours it really took, given those six facts. Predict 0.1, 0.5, 0.9. Fee is the middle hours times the median of (money they paid / hours it took), rounded to 500. If the Prior Labs key is missing, similar jobs fill the stub and the pad says so.

**The sentence.** Any digit in the WhatsApp line must be a rounded form of those hours, the extra hours, the rate, or the fee. Fail once, try again; fail again, drop the prose.

**The backtest.** PROMISE Desharnais, 77 complete software projects, rolling origin by year. Mean vs linear vs similar-jobs vs TabPFN-3.5 when the key is present. The table lives in `eval/REPORT.md`. Analog MAE 1972 hours, linear 2013, mean 3114, n=46. TabPFN was not run in that file because this laptop had no token yet. I left that row empty on purpose.

**Sentry.** `gen_ai` spans on read, fit/predict, and the optional sentence, with model name, token counts, and the hours. Conversation text is not sent.

The pad is a yellow carbon-copy notebook because that is the object this replaces, not a dashboard.

## Why Does Open Innovation Matter?

Closed quote tools want the ask, and they bill per call. After month one you are renting your own memory.

TabPFN is a foundation model for tables the size of a freelancer's year. You cannot get that from a general chat API without uploading every past client's ask as few-shot text. The open tabular weights (and the hosted 3.5 API on the free tier) are what make "fit on my 40 rows, emit a band, cost nothing per quote" a product instead of a demo.

Gemma's weights are open, so the reader is swappable. Today it runs on AI Studio because this laptop has 4 GB of RAM and will not host a 12B model. That sentence belongs in the post. Pretending otherwise would be the dishonest version of "runs locally."

The digit check is only possible because the hours come from a model whose output is a short list of numbers. A chatbot quote has no such list.

Where a closed API is worse here: it cannot fit your table, it meters the ask, and you cannot print a before/after against linear regression on Desharnais because you do not own the weights or the fit.

## My Agent Session

*(embed Entire / DevRelay here if captured)*

## My First User

A freelancer I already know. Twenty minutes. No signup. They type three jobs or drop a file. They paste one ask they would send this week. They look at the red number.

Three questions, verbatim answers, here after the session on 18 October:

1. Would you pay Rs 499 a month for this?
2. What did it get wrong?
3. What do you want it to tell you next?

If they did not pay, I will say so.

## Prize Categories

- Best Use of TabPFN
- Best Use of Gemma
- Best Use of Render
