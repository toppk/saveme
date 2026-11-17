#!/usr/bin/env bash
# Write redirect stubs for the old MkDocs URLs: site/redirects.sh OUT BASE [--root].
# BASE is where the new pages live (".." on Pages, the Pages URL for Read the Docs).
# --root also redirects / and 404.html, for a host that only redirects.
set -euo pipefail

out=$1 base=$2 root=${3-}
canonical=https://toppk.github.io/saveme

stub() {
  local file=$1 target=$2
  mkdir -p "$(dirname "$file")"
  cat >"$file" <<EOF
<!doctype html>
<meta charset="utf-8">
<title>saveme docs moved</title>
<link rel="canonical" href="$canonical/$target">
<script>location.replace("$base/$target" + location.hash)</script>
<meta http-equiv="refresh" content="0; url=$base/$target">
<p>The saveme docs moved to <a href="$canonical/$target">$canonical/$target</a>.</p>
EOF
}

stub "$out/GETTING_STARTED/index.html" getting-started.html
stub "$out/USAGE/index.html" usage.html
if [[ "$root" == --root ]]; then
  stub "$out/index.html" ""
  stub "$out/404.html" ""
fi
