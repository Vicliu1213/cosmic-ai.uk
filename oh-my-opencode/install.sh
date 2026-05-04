#!/usr/bin/env bash
set -euo pipefail

OH_MY_OPENCODE_DIR="${OH_MY_OPENCODE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export OH_MY_OPENCODE_DIR

source "${OH_MY_OPENCODE_DIR}/oh-my-opencode.sh"
