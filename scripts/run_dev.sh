#!/usr/bin/env bash
# Run the daemon locally with mock adapter.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python -m hummbl_broadcast.daemon --config examples/config.mock.toml --dry-run
