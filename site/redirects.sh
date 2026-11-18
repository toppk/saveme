#!/usr/bin/env bash
# Write redirect stubs for the old MkDocs URLs: site/redirects.sh OUT.
set -euo pipefail

out=$1
canonical=https://toppk.github.io/saveme

stub() {
  local file=$1 target=$2
  mkdir -p "$(dirname "$file")"
  cat >"$file" <<HTML
<!doctype html>
<meta charset="utf-8">
<title>saveme docs moved</title>
<link rel="canonical" href="$canonical/$target">
<script>location.replace("../$target" + location.hash)</script>
<meta http-equiv="refresh" content="0; url=../$target">
<p>The saveme docs moved to <a href="$canonical/$target">$canonical/$target</a>.</p>
HTML
}

stub "$out/GETTING_STARTED/index.html" getting-started.html
stub "$out/USAGE/index.html" usage.html
