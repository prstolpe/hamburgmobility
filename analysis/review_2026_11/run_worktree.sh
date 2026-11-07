#!/usr/bin/env bash
# Review 2026-11: run the pipeline in an isolated git worktree so that data/interim, data/out, config/
# and pipeline/ of the main checkout stay untouched.
#
# Usage: run_worktree.sh <name> <FROM-stage> [ref] [patch-file]
#   name        worktree ../SFP_wt_<name>; log to data/scenarios/<name>/run.log
#   FROM-stage  first street stage for make rerun (network, conflate, ..., classify)
#   ref         git ref to check out (default HEAD)
#   patch-file  optional patch applied in the worktree only (rule changes for scenarios)
# Env: SFP_WORKERS is passed through; SEED_INTERIM=1 copies data/interim/*.parquet first (needed when
# FROM is later than network); WARM_CACHE=1 copies data/interim/cache (default: cold cache).
set -euo pipefail

name=$1; from=$2; ref=${3:-HEAD}; patch=${4:-}
main=$(cd "$(dirname "$0")/../.." && pwd)
wt="$main/../SFP_wt_$name"
out="$main/data/scenarios/$name"
mkdir -p "$out"

if [ ! -d "$wt" ]; then
  git -C "$main" worktree add --detach "$wt" "$ref" >/dev/null
fi
mkdir -p "$wt/data/interim" "$wt/data/out"
ln -sfn "$main/data/raw" "$wt/data/raw"
ln -sfn "$main/data/baseline" "$wt/data/baseline"
ln -sfn "$main/.venv" "$wt/.venv"
if [ "${SEED_INTERIM:-0}" = 1 ]; then cp "$main"/data/interim/*.parquet "$wt/data/interim/"; fi
if [ "${WARM_CACHE:-0}" = 1 ]; then cp -R "$main/data/interim/cache" "$wt/data/interim/"; fi
if [ -n "$patch" ]; then git -C "$wt" apply "$patch"; fi

cd "$wt"
export UV_NO_SYNC=1
{
  echo "worktree=$wt ref=$(git rev-parse --short HEAD) from=$from workers=${SFP_WORKERS:-all} start=$(date -Iseconds)"
  # timestamp every line so stage run times can be read from the log
  /usr/bin/time -l make rerun FROM="$from" 2>&1 | while IFS= read -r l; do printf '%s %s\n' "$(date +%H:%M:%S)" "$l"; done
  echo "end=$(date -Iseconds)"
} > "$out/run.log" 2>&1
