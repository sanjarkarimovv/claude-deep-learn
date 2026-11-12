#!/bin/bash
# Kunlik eslatmalarni yoqadi.
# macOS TCC ~/Desktop ni himoyalaydi va launchd dan ishga tushgan python3 uni
# oʻqiy olmasligi mumkin. Shuning uchun script lar ~/.claude-deep-learn ga
# nusxalanadi, holat esa state.json nusxasidan oʻqiladi.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$HOME/.claude-deep-learn"
LABEL="com.claude-deep-learn.reminder"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$STATE_DIR" "$HOME/Library/LaunchAgents"
cp "$REPO/scripts/remind.py" "$REPO/scripts/progress.py" "$STATE_DIR/"
/usr/bin/python3 "$REPO/scripts/progress.py" status > /dev/null  # state.json ni yangilaydi

{
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>$STATE_DIR/remind.py</string>
  </array>
  <key>StandardOutPath</key><string>$STATE_DIR/remind.log</string>
  <key>StandardErrorPath</key><string>$STATE_DIR/remind.log</string>
  <key>StartCalendarInterval</key>
  <array>
EOF
  for hour in $(seq 9 23); do
    printf '    <dict><key>Hour</key><integer>%d</integer><key>Minute</key><integer>0</integer></dict>\n' "$hour"
  done
  printf '    <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>59</integer></dict>\n'
  cat <<EOF
  </array>
</dict>
</plist>
EOF
} > "$PLIST"

plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "✅ Eslatmalar yoqildi: har kuni 09:00–23:59 (yakshanbadan tashqari)."
echo "   Test: /usr/bin/python3 $STATE_DIR/remind.py --test"
