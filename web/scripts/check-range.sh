#!/usr/bin/env bash
# Checks HTTP range requests for the PMTiles files at a deployed site: ./check-range.sh https://owner.github.io/repo/
set -euo pipefail
base="${1:?Usage: check-range.sh <site-url>}"
base="${base%/}"
fail=0
for f in tiles/segments.pmtiles basemap/basemap.pmtiles; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -r 0-126 "$base/$f")
  if [ "$code" = "206" ]; then echo "ok   $f (206 Partial Content)"; else echo "FAIL $f (HTTP $code, erwartet 206)"; fail=1; fi
done
exit $fail
