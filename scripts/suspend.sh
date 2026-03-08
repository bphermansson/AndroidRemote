#!/usr/bin/env bash
set -euo pipefail

# Force suspend for remote use: ignore desktop inhibitors.
if /usr/bin/systemctl suspend -i; then
  exit 0
fi

# Fallback for some systems.
if /usr/bin/loginctl sleep; then
  exit 0
fi

echo mem > /sys/power/state
