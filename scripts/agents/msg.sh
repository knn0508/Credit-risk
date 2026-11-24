#!/usr/bin/env bash
# İstifadə: scripts/agents/msg.sh <kimdən: 01-06 və ya me> <kimə: 01-06> "mesaj"
set -euo pipefail
[ $# -ge 3 ] || { echo "İstifadə: $0 <kimdən> <kimə> \"mesaj\""; exit 1; }
FROM="$1"; TO="$2"; shift 2; MSG="$*"
TOP="$(git rev-parse --show-toplevel)"
COMMS="$TOP/.agents"
SESSION="$(cat "$COMMS/SESSION" 2>/dev/null || echo credit)"
TS="$(date '+%F %H:%M')"
[ -f "$COMMS/inbox-$TO.md" ] || { echo "Naməlum agent: $TO"; exit 1; }

printf '\n## [%s] %s -> %s\n%s\n' "$TS" "$FROM" "$TO" "$MSG" >> "$COMMS/inbox-$TO.md"
printf '[%s] %s -> %s: %s\n' "$TS" "$FROM" "$TO" "$MSG" >> "$COMMS/log.md"

WIN="$(tmux list-windows -t "$SESSION" -F '#{window_name}' 2>/dev/null | grep "^$TO-" | head -1 || true)"
if [ -n "$WIN" ]; then
  tmux send-keys -t "$SESSION:$WIN" -l "Agent $FROM-dən yeni mesaj var: .agents/inbox-$TO.md faylını oxu və uyğun hərəkət et."
  sleep 0.5
  tmux send-keys -t "$SESSION:$WIN" Enter
  echo "Göndərildi: $FROM -> $TO (pəncərə $WIN)"
else
  echo "Inbox-a yazıldı, amma tmux pəncərəsi tapılmadı (agent işləmir?)."
fi
