# You said 10. It took 19.

This is not a machine that invents a price.

It is a notebook. You write what you promised. You write what it really took. The red number is hours you worked and did not charge for. Next time someone asks, we look at that notebook and stop you promising 10 again.

## If you have a spreadsheet, a photo, a PDF, or nothing

You do not need a file. Remember three jobs in your head and type them. If you do have a file, drop it — Excel, photo of a notebook, PDF, Word, JSON, or CSV. If we cannot read it, type the jobs on the left.

- What it was called
- Hours you promised
- Hours it really took
- Money they paid, if you remember (you can leave this blank)

Press **Add to Quoted** each time. After three, paste what the next person asked for.

If you want to try Quoted before adding your own jobs, press **See an example notebook**.

## Try it

Open http://127.0.0.1:5173

- You start on **your** notebook, empty. Add jobs you already finished, or import a file.
- After three jobs, click **Dentist website by Friday**, then **What should I promise this time?**
- **See an example notebook** is optional, if you want to look before writing yours.

## Who pays

Anyone who works for themselves and keeps saying yes too cheap. Rs 499 a month. The first unpaid week they stop giving away pays for the year.

Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle.

## Run

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r api\requirements.txt
copy .env.example .env
cd api
python -m uvicorn main:app --reload --port 8000
```

```
cd web
npm install
npm run dev
```

Keys are optional. See `docs/deploy.md`.
