#!/bin/sh
set -e

echo "==> Rodando migrations..."
alembic upgrade head

echo "==> Populando banco de dados..."
python seed.py

echo "==> Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
