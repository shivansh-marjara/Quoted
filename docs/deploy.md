# Deploy Quoted

## Only you can finish this

The pad, the importer, the post draft, and Render/Docker files are already in the repo. These steps need your accounts:

1. Keys in `.env` (copy from `.env.example`): `TABPFN_TOKEN` from https://platform.priorlabs.ai and `GEMINI_API_KEY` from https://aistudio.google.com/apikey. Optional: `SENTRY_DSN`.
2. Put the project on GitHub. Create a Render Blueprint from `render.yaml`. Set the same keys as secrets.
3. Paste the live URL and GitHub URL into `submission/DEV_POST.md` (Demo + `{% github %}`).
4. Sit with one freelancer (`docs/first-user.md`). Paste their three answers into **My First User**.
5. Publish the post on DEV before 18 Oct 2026 23:59 PDT with `#devchallenge` and `#hf26challenge`.

## Keys (free)

1. TabPFN: https://platform.priorlabs.ai — set `TABPFN_TOKEN`.
2. Gemma: https://aistudio.google.com/apikey — set `GEMINI_API_KEY`. Try `GEMMA_MODEL=gemma-3-12b-it`. If that model is not on the key, set `gemma-3-27b-it` or the Gemma 3 name shown in AI Studio.
3. Sentry: create a project, set `SENTRY_DSN`.
4. `.tech` domain: claim the Hacktoberfest promo at https://hacktoberfest.com/my/promos and point `quoted.tech` (or `getquoted.tech`) at the Render URL.

Without TabPFN the Quote still fills, using k-NN analogy on History, and the stub labels the predictor `analog`. Without Gemma, a rule extractor fills the Feature Row and the stub labels `rule`.

## Render

```
render.yaml
```

Create a Blueprint from the GitHub repo. Set the three secrets. The Docker image serves the pad and the API on one free web service.

Health: `GET /api/health`.

## Local

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r api/requirements.txt
cd api
uvicorn main:app --reload --port 8000
```

In another terminal:

```
cd web
npm install
npm run dev
```

Open http://127.0.0.1:5173

## Commits after the deadline

If anything is committed after 18 October 2026 23:59 PDT, list the SHAs in this file. None yet.
