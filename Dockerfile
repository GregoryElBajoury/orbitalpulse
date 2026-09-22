# --- Stage 1 : Build & Dependencies communes ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2 : Runtime pour le Collector ---
FROM python:3.11-slim AS collector-runtime

WORKDIR /app

RUN useradd -u 10001 collector && \
    chown -R collector:collector /app

COPY --from=builder /install /usr/local
COPY . .

USER collector
CMD ["python", "collector.py"]

# --- Stage 3 : Runtime pour l'Interface Streamlit (UI) ---
FROM python:3.11-slim AS ui-runtime

WORKDIR /app

RUN useradd -u 10002 streamlituser && \
    chown -R streamlituser:streamlituser /app

COPY --from=builder /install /usr/local
COPY . .

USER streamlituser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]