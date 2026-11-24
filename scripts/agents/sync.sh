#!/usr/bin/env bash
# Öz agent branch-ına main-in son vəziyyətini gətirir. Worktree-dən işlət.
set -euo pipefail
BR="$(git rev-parse --abbrev-ref HEAD)"
[ "$BR" != "main" ] || { echo "main-də sync lazım deyil"; exit 1; }
git merge --no-edit main
echo "OK: $BR <- main"
