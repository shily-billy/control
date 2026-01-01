#!/usr/bin/env bash
set -euo pipefail

# Clear proxy-related env vars that break pip/playwright downloads.
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy no_proxy NO_PROXY

# Re-run command passed to this script.
exec "$@"
