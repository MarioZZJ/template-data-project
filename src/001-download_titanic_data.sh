#!/usr/bin/env bash
# Purpose: List and download the two official Titanic competition data files safely.
# Inputs: Kaggle competition access plus OAuth, KAGGLE_API_TOKEN, access_token, or kaggle.json authentication.
# Outputs: data/raw/titanic/train.csv and data/raw/titanic/test.csv (ignored by Git).
# Run: bash src/001-download_titanic_data.sh [--force]
# Proxy fallback: KAGGLE_STORAGE_TLS_HOST=storage.cloud.google.com bash src/001-download_titanic_data.sh

set -euo pipefail

usage() {
  echo "Usage: bash src/001-download_titanic_data.sh [--force]" >&2
}

auth_help() {
  cat >&2 <<'MSG'
Kaggle access failed.

1. Sign in to Kaggle and accept the Titanic competition rules.
2. Configure one supported authentication method without pasting a token into this repository:
   kaggle auth login
   export KAGGLE_API_TOKEN='<token from Kaggle settings>'
   place the token in ~/.kaggle/access_token
   or place legacy credentials in ~/.kaggle/kaggle.json
3. Re-run this script.
If authentication works but downloads fail, check network access to api.kaggle.com and storage.googleapis.com.
MSG
}

force=0
timeout_seconds="${KAGGLE_TIMEOUT_SECONDS:-60}"
case "${1:-}" in
  "") ;;
  --force) force=1 ;;
  *) usage; exit 2 ;;
esac

if [[ $# -gt 1 ]]; then
  usage
  exit 2
fi

if ! command -v kaggle >/dev/null 2>&1; then
  echo "Missing required command: kaggle" >&2
  echo "Install the official Kaggle CLI outside the project environment, then retry." >&2
  exit 1
fi

if ! command -v sha256sum >/dev/null 2>&1; then
  echo "Missing required command: sha256sum" >&2
  exit 1
fi

if [[ ! "$timeout_seconds" =~ ^[1-9][0-9]*$ ]]; then
  echo "KAGGLE_TIMEOUT_SECONDS must be a positive integer" >&2
  exit 2
fi

run_kaggle() {
  if command -v timeout >/dev/null 2>&1; then
    timeout --foreground "${timeout_seconds}s" kaggle "$@"
  else
    kaggle "$@"
  fi
}

download_with_oauth_curl() {
  local filename="$1"
  local target="$2"
  local tls_host="${KAGGLE_STORAGE_TLS_HOST:-}"
  local token header_file temp_file payload location alternate_location redirect_host

  if [[ -z "$tls_host" ]]; then
    return 1
  fi
  if [[ "$tls_host" != "storage.cloud.google.com" ]]; then
    echo "Unsupported KAGGLE_STORAGE_TLS_HOST: $tls_host" >&2
    return 1
  fi
  if ! command -v curl >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
    echo "The OAuth storage fallback requires curl and python3." >&2
    return 1
  fi
  if ! token="$(kaggle auth print-access-token 2>/dev/null)"; then
    echo "Unable to obtain an in-memory Kaggle OAuth access token for the storage fallback." >&2
    return 1
  fi
  if [[ -z "$token" || "$token" == *[[:space:]]* ]]; then
    echo "Kaggle returned an invalid access-token response." >&2
    unset token
    return 1
  fi

  header_file="$(mktemp /tmp/kaggle-headers.XXXXXX)"
  temp_file="$(mktemp "$target_dir/.${filename}.XXXXXX")"
  payload="$(printf '{\"competitionName\":\"titanic\",\"fileName\":\"%s\"}' "$filename")"

  if ! printf 'header = "Authorization: Bearer %s"\n' "$token" | curl \
    --config - \
    --fail \
    --silent \
    --show-error \
    --retry 3 \
    --retry-all-errors \
    --retry-delay 1 \
    --connect-timeout 10 \
    --max-time "$timeout_seconds" \
    --request POST \
    --header 'Content-Type: application/json' \
    --data-binary "$payload" \
    --max-redirs 0 \
    --dump-header "$header_file" \
    --output /dev/null \
    'https://api.kaggle.com/v1/competitions.CompetitionApiService/DownloadDataFile'; then
    unset token
    unlink "$header_file" "$temp_file"
    return 1
  fi
  unset token payload

  if ! location="$(HEADER_FILE="$header_file" python3 -c 'import os; from pathlib import Path; lines=Path(os.environ["HEADER_FILE"]).read_text(errors="replace").splitlines(); print(next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("location:")), ""))')"; then
    unlink "$header_file" "$temp_file"
    return 1
  fi
  redirect_host="$(LOCATION="$location" python3 -c 'import os; from urllib.parse import urlsplit; print(urlsplit(os.environ["LOCATION"]).hostname or "")')"
  if [[ "$redirect_host" != "storage.googleapis.com" ]]; then
    echo "Unexpected Kaggle download redirect host: $redirect_host" >&2
    unset location
    unlink "$header_file" "$temp_file"
    return 1
  fi
  alternate_location="$(LOCATION="$location" TLS_HOST="$tls_host" python3 -c 'import os; from urllib.parse import urlsplit, urlunsplit; value=urlsplit(os.environ["LOCATION"]); print(urlunsplit((value.scheme, os.environ["TLS_HOST"], value.path, value.query, value.fragment)))')"
  unset location redirect_host

  if ! printf 'url = "%s"\n' "$alternate_location" | curl \
    --config - \
    --http1.1 \
    --header 'Host: storage.googleapis.com' \
    --fail \
    --silent \
    --show-error \
    --retry 3 \
    --retry-all-errors \
    --retry-delay 1 \
    --connect-timeout 10 \
    --max-time "$timeout_seconds" \
    --output "$temp_file"; then
    unset alternate_location
    unlink "$header_file" "$temp_file"
    return 1
  fi
  unset alternate_location

  if [[ ! -s "$temp_file" ]]; then
    echo "OAuth storage fallback produced an empty file: $filename" >&2
    unlink "$header_file" "$temp_file"
    return 1
  fi
  mv "$temp_file" "$target"
  unlink "$header_file"
  echo "Downloaded $filename through the official OAuth API with TLS host fallback."
}

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
data_root="${DATA_ROOT:-$repo_root/data}"
if [[ "$data_root" != /* ]]; then
  data_root="$repo_root/${data_root#./}"
fi
target_dir="$data_root/raw/titanic"
mkdir -p "$target_dir"

echo "Checking official competition file listing."
if run_kaggle competitions files titanic; then
  :
else
  status=$?
  if [[ "$status" -eq 124 ]]; then
    echo "Kaggle file listing timed out after ${timeout_seconds} seconds." >&2
  fi
  auth_help
  exit 1
fi

download_file() {
  local filename="$1"
  local target="$target_dir/$filename"
  local -a options=(titanic -f "$filename" -p "$target_dir")

  if [[ -s "$target" && "$force" -eq 0 ]]; then
    echo "Keeping existing non-empty raw file: $target"
    return
  fi

  if [[ -e "$target" && "$force" -eq 0 ]]; then
    echo "Refusing to replace existing file without --force: $target" >&2
    exit 1
  fi

  if [[ "$force" -eq 1 ]]; then
    options+=(-o)
  fi

  echo "Downloading $filename."
  if run_kaggle competitions download "${options[@]}"; then
    :
  else
    status=$?
    if [[ "$status" -eq 124 ]]; then
      echo "Kaggle download timed out after ${timeout_seconds} seconds: $filename" >&2
    else
      echo "Official Kaggle CLI download failed with exit code $status: $filename" >&2
    fi
    if download_with_oauth_curl "$filename" "$target"; then
      :
    else
      auth_help
      exit 1
    fi
  fi

  if [[ ! -s "$target" ]]; then
    echo "Download command completed but expected file is missing or empty: $target" >&2
    exit 1
  fi
}

download_file train.csv
download_file test.csv

for filename in train.csv test.csv; do
  path="$target_dir/$filename"
  size="$(wc -c < "$path" | tr -d ' ')"
  digest="$(sha256sum "$path" | awk '{print $1}')"
  printf '%s\tsize_bytes=%s\tsha256=%s\n' "$filename" "$size" "$digest"
done
