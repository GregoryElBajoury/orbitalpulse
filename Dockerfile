# --- Stage 1 : Build & Dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Installation des dépendances de compilation si nécessaire
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2 : Runtime sécurisé ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Création d'un utilisateur non-privilégié
RUN useradd -u 10001 collector && \
    chown -R collector:collector /app

# Copie des dépendances installées depuis le builder
COPY --from=builder /install /usr/local

# Copie du code source
COPY . .

# Passage à l'utilisateur non-root
USER collector

CMD ["python", "collector.py"]