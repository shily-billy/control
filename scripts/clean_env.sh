#!/usr/bin/env bash
set -euo pipefail

# Usage: source scripts/clean_env.sh
# Clears proxy-related env vars in current shell.
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy no_proxy NO_PROXY

echo "[clean_env] proxy env vars cleared"
