#!/usr/bin/env bash
# Install pre-push hook for hummbl-broadcast.
# Catches the "side-channel-ship" antipattern where a file is ssh/scp'd to
# a remote before being committed locally, causing git pull to fail.
#
# Re-run after cloning this repo, or after pulling a new version of
# ~/.agents/scripts/check-side-channel-ship.py.
set -euo pipefail
SCRIPT_SRC="$HOME/.agents/scripts/check-side-channel-ship.py"
HOOK_DST="$(git rev-parse --show-toplevel)/.git/hooks/pre-push"

if [ ! -f "$SCRIPT_SRC" ]; then
  echo "Missing $SCRIPT_SRC — install it first or run on a machine with .agents synced."
  exit 1
fi

cp "$SCRIPT_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "Installed pre-push hook at $HOOK_DST"
echo "Test: create an untracked file in scripts/ and try git push."
