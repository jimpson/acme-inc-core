#!/usr/bin/env bash
# Stop hook: after the agent finishes, run the convention gate (fast, static-only)
# against the working tree - including untracked files the agent just wrote. On a
# violation, feed the failures back so the agent self-corrects in the same session.
# Fails open: any hook-internal error never blocks the developer.
input=$(cat)  # consume stop-event JSON (unused)
cd "$(dirname "$0")/../.." 2>/dev/null || exit 0

PY="$(command -v python3 || true)"
[ -z "$PY" ] && exit 0

out="$("$PY" tools/ci_gate.py --base origin/main --no-tests 2>&1)"
code=$?

if [ "$code" -ne 0 ]; then
  msg="$(printf '%s' "$out" | "$PY" -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
  printf '{"followup_message": %s, "user_message": "Convention gate found issues - the agent will correct them."}\n' "$msg"
  exit 0
fi
exit 0
