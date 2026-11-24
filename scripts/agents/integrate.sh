#!/usr/bin/env bash
# İstifadə: scripts/agents/integrate.sh agent/02-data    (yalnız Agent 01 / insan)
# main worktree-də agent branch-ını --no-ff merge edir. İstənilən worktree-dən işləyir.
set -euo pipefail
BR="${1:?İstifadə: integrate.sh agent/NN-xxx}"
MAIN="$(git worktree list --porcelain | awk 'NR==1{print $2}')"
[ "$(git -C "$MAIN" rev-parse --abbrev-ref HEAD)" = "main" ] || { echo "$MAIN main-də deyil"; exit 1; }
git -C "$MAIN" diff --quiet && git -C "$MAIN" diff --cached --quiet || { echo "main təmiz deyil"; exit 1; }
git -C "$MAIN" merge --no-ff "$BR" -m "integrate: $BR"
echo "OK: $BR -> main. Digər agentlər: scripts/agents/sync.sh"
