#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${HERMES_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
HB_DIR="${HUMMINGBOT_DIR:-${ROOT_DIR}/.hermes/hummingbot/vendor/hummingbot}"

if [ ! -d "${HB_DIR}" ]; then
  printf 'Hummingbot source not installed at %s\n' "${HB_DIR}" >&2
  printf 'Install it first or set HUMMINGBOT_DIR.\n' >&2
  exit 1
fi

cd "${HB_DIR}"
exec "./start" "$@"
