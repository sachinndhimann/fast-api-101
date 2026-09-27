#!/usr/bin/env bash
# Exercises chapter1's Products API. Run the app first:
#   uvicorn main:app --reload --port 8000
set -euo pipefail
BASE=http://localhost:8000

echo "-- create --"
curl -s -X POST $BASE/products -H 'Content-Type: application/json' \
  -d '{"name":"Wireless Mouse","price_cents":1999,"category":"electronics"}' | tee /tmp/product.json
ID=$(python3 -c "import json;print(json.load(open('/tmp/product.json'))['id'])")

echo "-- list --"
curl -s "$BASE/products?category=electronics" ; echo

echo "-- get one --"
curl -s "$BASE/products/$ID" ; echo

echo "-- patch --"
curl -s -X PATCH "$BASE/products/$ID" -H 'Content-Type: application/json' -d '{"in_stock": false}' ; echo

echo "-- delete --"
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE "$BASE/products/$ID"
