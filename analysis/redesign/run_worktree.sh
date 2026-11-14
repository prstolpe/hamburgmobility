#!/usr/bin/env bash
# Redesign (prompt 24): dry run in an isolated worktree via analysis/review_2026_11/run_worktree.sh, then collect
# the results under data/scenarios/redesign/<name>/ (run.log, interim/*.parquet, out_hashes.txt).
#
# Usage: run_worktree.sh <name> <FROM-stage> [patch-file]
#   The worktree is ../SFP_wt_redesign_<name> at the current HEAD; it is removed after the results are copied.
# Env: SEED_INTERIM and WARM_CACHE as in the review script (both default to 1 here).
set -euo pipefail

name=$1; from=$2; patch=${3:-}
main=$(cd "$(dirname "$0")/../.." && pwd)
dest="$main/data/scenarios/redesign/$name"
wt="$main/../SFP_wt_redesign_$name"
mkdir -p "$dest"

SEED_INTERIM=${SEED_INTERIM:-1} WARM_CACHE=${WARM_CACHE:-1} \
  "$main/analysis/review_2026_11/run_worktree.sh" "redesign_$name" "$from" HEAD "${patch:+$(cd "$(dirname "$patch")" && pwd)/$(basename "$patch")}"

mv "$main/data/scenarios/redesign_$name/run.log" "$dest/run.log"
rmdir "$main/data/scenarios/redesign_$name"
mkdir -p "$dest/interim"
cp "$wt"/data/interim/*.parquet "$dest/interim/"
(cd "$wt/data/out" && find . -type f ! -name '*.pmtiles' -print0 | sort -z | xargs -0 shasum -a 256) > "$dest/out_hashes.txt"
if [ -n "$patch" ]; then cp "$patch" "$dest/"; fi
git -C "$main" worktree remove --force "$wt"
echo "done: $dest"
