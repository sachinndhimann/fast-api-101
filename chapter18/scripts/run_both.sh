#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
(PYTHONPATH=app/users_service uvicorn main:app --port 8001 &)
(PYTHONPATH=app/orders_service USERS_SERVICE_URL=http://localhost:8001 uvicorn main:app --port 8002 &)
echo "Users on :8001, Orders on :8002"
