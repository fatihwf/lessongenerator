#!/bin/bash
# Start the Bloom-aware Lesson Generator FastAPI service
set -e

cd /home/runner/workspace/services/bloom-api
export PYTHONPATH=/home/runner/workspace/services/bloom-api

exec /home/runner/workspace/.pythonlibs/bin/uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8080}" \
  --reload \
  --log-level info
