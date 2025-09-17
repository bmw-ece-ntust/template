#!/usr/bin/env bash
set -Eeuo pipefail


# === Defaults (edit if you want; or override via flags) ===
REGISTRY="${REGISTRY:-192.168.8.84}"     # host or host:port (no scheme)
PROJECT="${PROJECT:-library}"
IMAGE="${IMAGE:-ta-rapp}"
TAG="${TAG:-1.0.5}"
CONTEXT="${CONTEXT:-.}"
SCHEME="${SCHEME:-https}"                # https is recommended
CERT_FILE="${CERT_FILE:-./scripts/ca.crt}"       # CA file sits next to this script
PLATFORMS="${PLATFORMS:-}"               # e.g. linux/amd64,linux/arm64

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
CERT_FILE="${CERT_FILE:-"${SCRIPT_DIR}/ca.crt"}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]
  -r, --registry   <host[:port]>   (default: $REGISTRY)
  -p, --project    <name>          (default: $PROJECT)
  -i, --image      <name>          (default: $IMAGE)
  -t, --tag        <tag>           (default: $TAG)
  -c, --context    <path>          (default: $CONTEXT)
      --http                      Use HTTP (not recommended)
      --platforms  <list>         e.g. linux/amd64,linux/arm64
      --cert       <path>         CA path (default: ./ca.crt)
  -h, --help
NOTE: Credentials are taken ONLY from the USER CONFIG block at the top.
EOF
}

info()  { printf "\033[1;34m[INFO]\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m[ERR ]\033[0m %s\n" "$*" >&2; }

# --- Parse args (no auth flags; creds come from top-of-file) ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--registry) REGISTRY="$2"; shift 2;;
    -p|--project)  PROJECT="$2"; shift 2;;
    -i|--image)    IMAGE="$2"; shift 2;;
    -t|--tag)      TAG="$2"; shift 2;;
    -c|--context)  CONTEXT="$2"; shift 2;;
    --http)        SCHEME="http"; shift 1;;
    --platforms)   PLATFORMS="$2"; shift 2;;
    --cert)        CERT_FILE="$2"; shift 2;;
    -h|--help)     usage; exit 0;;
    *) error "Unknown argument: $1"; usage; exit 2;;
  esac
done

# Read creds from env (exported by Makefile via make.local)
HARBOR_USER="${HARBOR_USER:-}"
HARBOR_PASSWORD="${HARBOR_PASSWORD:-}"
if [[ -z "$HARBOR_USER" || -z "$HARBOR_PASSWORD" ]]; then
  echo "[ERR ] HARBOR_USER/HARBOR_PASSWORD are empty. Set them in make.local (exported by Makefile)." >&2
  exit 2
fi


# Normalize ports vs scheme
if [[ "$SCHEME" == "https" && "$REGISTRY" == *":80" ]]; then
  warn "HTTPS selected but registry ends with :80 → switching to ${REGISTRY%:80}"
  REGISTRY="${REGISTRY%:80}"
fi
if [[ "$SCHEME" == "http" && "$REGISTRY" == *":443" ]]; then
  warn "HTTP selected but registry ends with :443 → switching to ${REGISTRY%:443}"
  REGISTRY="${REGISTRY%:443}"
fi

FULL_REF="${REGISTRY}/${PROJECT}/${IMAGE}:${TAG}"

# --- Preflight tools/files ---
command -v docker >/dev/null 2>&1 || { error "docker is not installed."; exit 1; }
docker buildx version >/dev/null 2>&1 || { error "Docker Buildx not available."; exit 1; }
command -v curl >/dev/null 2>&1 || { error "curl is required."; exit 1; }
[[ -f "${CONTEXT}/Dockerfile" ]] || { error "Dockerfile not found in ${CONTEXT}"; exit 1; }
[[ "$SCHEME" == "http" ]] || [[ -f "${CERT_FILE}" ]] || { error "CA file not found: ${CERT_FILE}"; exit 1; }

# --- Require creds from the top-of-file block ---
if [[ -z "$HARBOR_USER" || -z "$HARBOR_PASSWORD" ]]; then
  error "HARBOR_USER/HARBOR_PASSWORD are empty. Edit this script's USER CONFIG block (top of file) and re-run."
  exit 2
fi

# --- CA install/skip logic (Docker certs.d) ---
host="${REGISTRY%:*}"
port=""
[[ "$REGISTRY" == *:* ]] && port="${REGISTRY##*:}"

is_ca_installed_linux() {
  local base="/etc/docker/certs.d"
  [[ -f "${base}/${host}/ca.crt" ]] || return 1
  if [[ -n "$port" ]]; then
    [[ -f "${base}/${host}:${port}/ca.crt" ]] || return 1
  else
    [[ -f "${base}/${host}:443/ca.crt" ]] || return 1
  fi
  return 0
}
is_ca_installed_mac() {
  local base="$HOME/Library/Group Containers/group.com.docker/certs.d"
  [[ -f "${base}/${host}/ca.crt" ]] || return 1
  if [[ -n "$port" ]]; then
    [[ -f "${base}/${host}:${port}/ca.crt" ]] || return 1
  else
    [[ -f "${base}/${host}:443/ca.crt" ]] || return 1
  fi
  return 0
}
install_ca_linux() {
  local base="/etc/docker/certs.d"
  local sudo_cmd=""; [[ $EUID -ne 0 ]] && sudo_cmd="sudo"
  $sudo_cmd mkdir -p "${base}/${host}" && $sudo_cmd cp -f "${CERT_FILE}" "${base}/${host}/ca.crt"
  info "Installed CA to ${base}/${host}/ca.crt"
  if [[ -n "$port" ]]; then
    $sudo_cmd mkdir -p "${base}/${host}:${port}" && $sudo_cmd cp -f "${CERT_FILE}" "${base}/${host}:${port}/ca.crt"
    info "Installed CA to ${base}/${host}:${port}/ca.crt"
  else
    $sudo_cmd mkdir -p "${base}/${host}:443" && $sudo_cmd cp -f "${CERT_FILE}" "${base}/${host}:443/ca.crt"
    info "Installed CA to ${base}/${host}:443/ca.crt"
  fi
  if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service | grep -q docker.service; then
    $sudo_cmd systemctl restart docker && info "Restarted Docker via systemd."
  elif command -v snap >/dev/null 2>&1 && snap list 2>/dev/null | grep -q '^docker '; then
    $sudo_cmd snap restart docker || true && info "Restarted Docker via snap."
  else
    $sudo_cmd service docker restart || true && info "Restarted Docker via service."
  fi
}
install_ca_mac() {
  local base="$HOME/Library/Group Containers/group.com.docker/certs.d"
  mkdir -p "${base}/${host}" && cp -f "${CERT_FILE}" "${base}/${host}/ca.crt"
  info "Installed CA to ${base}/${host}/ca.crt"
  if [[ -n "$port" ]]; then
    mkdir -p "${base}/${host}:${port}" && cp -f "${CERT_FILE}" "${base}/${host}:${port}/ca.crt"
    info "Installed CA to ${base}/${host}:${port}/ca.crt"
  else
    mkdir -p "${base}/${host}:443" && cp -f "${CERT_FILE}" "${base}/${host}:443/ca.crt"
    info "Installed CA to ${base}/${host}:443/ca.crt"
  fi
  warn "Please restart Docker Desktop to load the new CA (Docker Desktop → Quit & Reopen)."
}

ensure_ca() {
  [[ "$SCHEME" == "http" ]] && { warn "HTTP selected—skipping CA handling."; return; }
  case "$(uname -s)" in
    Linux)  is_ca_installed_linux && info "CA already present for ${REGISTRY}; skipping installation." || install_ca_linux ;;
    Darwin) is_ca_installed_mac   && info "CA already present for ${REGISTRY}; skipping installation." || install_ca_mac ;;
    *)      warn "Unsupported OS for auto CA install; continuing." ;;
  esac
}
ensure_ca

# --- Reachability probe (non-fatal; curl uses our CA) ---
CURL_ARGS=()
[[ "$SCHEME" == "https" && -f "$CERT_FILE" ]] && CURL_ARGS+=(--cacert "$CERT_FILE")
if curl -fsSI "${CURL_ARGS[@]}" "${SCHEME}://${REGISTRY}/v2/" >/dev/null 2>&1; then
  info "Registry reachable at ${SCHEME}://${REGISTRY}/v2/."
else
  warn "Registry probe via curl failed (SSL or connectivity). Continuing—Docker may still work."
fi

# --- Login (no prompts; uses top-of-file creds) ---
printf "%s" "$HARBOR_PASSWORD" | docker login "$REGISTRY" -u "$HARBOR_USER" --password-stdin
info "Login OK."

# --- Build + Push (Buildx) ---
build_args=( --push -t "${FULL_REF}" "${CONTEXT}" )
[[ -n "${PLATFORMS}" ]] && build_args=( --platform "${PLATFORMS}" "${build_args[@]}" )

info "Building and pushing ${FULL_REF} ..."
docker buildx build "${build_args[@]}"
info "Done. Pushed ${FULL_REF}"
