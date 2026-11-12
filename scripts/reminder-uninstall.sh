#!/bin/bash
# Kunlik eslatmalarni oʻchiradi. Holat fayllari ~/.claude-deep-learn da qoladi.
set -euo pipefail
LABEL="com.claude-deep-learn.reminder"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "🔕 Eslatmalar oʻchirildi."
