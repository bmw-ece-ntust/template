#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -z "${HEALTHCHECK_URL:-}" ]]; then
  echo "[ERR ] HEALTHCHECK_URL is not set. Set a GitHub secret or export before calling." >&2
  exit 2
fi

TIMEOUT="${HEALTHCHECK_TIMEOUT:-30}"
ATTEMPTS="${HEALTHCHECK_ATTEMPTS:-5}"
SLEEP="${HEALTHCHECK_SLEEP:-5}"

for (( i=1; i<=ATTEMPTS; i++ )); do
  if curl --fail --show-error --silent --max-time "${TIMEOUT}" "${HEALTHCHECK_URL}" >/tmp/healthcheck-response; then
    echo "[INFO] Health check succeeded on attempt ${i}."
    cat /tmp/healthcheck-response
    exit 0
  fi
  echo "[WARN] Attempt ${i} failed; retrying in ${SLEEP}s..." >&2
  sleep "${SLEEP}"
done

echo "[ERR ] Health check failed after ${ATTEMPTS} attempts." >&2
exit 1
