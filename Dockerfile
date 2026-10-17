FROM node:22-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install
COPY web/ ./
COPY samples/history.csv /web/public/samples/history.csv
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY api/ /app/api/
COPY samples/ /app/samples/
COPY eval/desharnais.csv /app/eval/desharnais.csv
COPY --from=web /web/dist /app/api/static
WORKDIR /app/api
EXPOSE 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
