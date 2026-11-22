#!/usr/bin/env bash
# Poll the bus forever with a maximum 1 s wait per iteration.
# Prints only a delivered message and exits 0; timeouts stay silent.
# Usage: tools/bus_loop.sh [NAME] [SINCE_ID]
set -u
NAME="${1:-script}"
SINCE="${2:-0}"
while true; do
  out="$(python3 tools/bus.py wait --as "$NAME" --since "$SINCE" --timeout 1 2>/dev/null)"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$out"
    exit 0
  fi
done
