#!/usr/bin/env bash
set -euo pipefail
BASE=http://localhost:8000
curl -s -X POST $BASE/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.com","password":"hunter22"}'; echo
TOKENS=$(curl -s -X POST $BASE/auth/login -d 'username=ada@example.com&password=hunter22')
echo "$TOKENS"
ACCESS=$(python3 -c "import json,sys;print(json.loads('''$TOKENS''')['access_token'])")
curl -s $BASE/users/me -H "Authorization: Bearer $ACCESS"; echo
