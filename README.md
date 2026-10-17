# Quoted

**You said 10. It took 19.**

You are a freelancer. They said the job was small. You said yes. You promised 10 hours. It took 19. You got paid for 10. The other hours were free. Quoted keeps those hours so you don't give them away twice.

Live: [quoted-32zd.onrender.com](https://quoted-32zd.onrender.com)

## How it works

1. Write jobs you already finished: what they asked, hours you promised, hours it took.
2. Paste the next thing they asked for.
3. Quoted looks at your jobs and tells you what to promise this time.

Gemma reads the ask. It does not pick the rupees. TabPFN looks at your finished jobs and predicts hours.

Type three jobs from memory, or drop Excel, a photo, a PDF, Word, or CSV.

## Run it yourself

Copy `.env.example` to `.env` and add `TABPFN_TOKEN` and `GEMINI_API_KEY` if you have them. The pad still runs without keys.

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r api\requirements.txt
cd api
python -m uvicorn main:app --reload --port 8000
```

```
cd web
npm install
npm run dev
```

Open http://127.0.0.1:5173
