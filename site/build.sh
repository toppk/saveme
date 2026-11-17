#!/usr/bin/env bash
# Build the documentation site with pandoc: site/build.sh [OUT] (default _site).
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(dirname "$here")
out=${1:-"$repo_root/_site"}
theme="$here/theme"
edit=${SAVEME_EDIT_URL-https://github.com/toppk/saveme/edit/master}
canonical=https://toppk.github.io/saveme

# Reading order: page|title|group|source. Presentation metadata is in meta/<page>.yaml.
pages=(
  "index|Overview|Start|docs/index.md"
  "getting-started|Getting started|Start|docs/GETTING_STARTED.md"
  "usage|Usage|Use|docs/USAGE.md"
)

field() { cut -d'|' -f"$2" <<<"$1"; }

nav_for() {
  local current=$1 group="" html="" p name title g
  for p in "${pages[@]}"; do
    name=$(field "$p" 1) title=$(field "$p" 2) g=$(field "$p" 3)
    if [[ "$g" != "$group" ]]; then
      [[ -n "$group" ]] && html+="</ul></div>"
      html+="<div class=\"nav-group\"><span class=\"nav-label\">$g</span><ul>"
      group=$g
    fi
    if [[ "$name" == "$current" ]]; then
      html+="<li><a href=\"$name.html\" aria-current=\"page\">$title</a></li>"
    else
      html+="<li><a href=\"$name.html\">$title</a></li>"
    fi
  done
  echo "$html</ul></div>"
}

rm -rf "$out"
mkdir -p "$out/theme" "$out/assets"
cp -r "$theme/horizon.css" "$theme/horizon.js" "$theme/fonts" "$out/theme/"
cp "$repo_root/docs/assets/"{logo-512.webp,logo-128.webp,favicon.ico} "$out/assets/"
cp "$here/llms.txt" "$out/llms.txt"
: >"$out/llms-full.txt"
touch "$out/.nojekyll"

count=${#pages[@]}
for i in "${!pages[@]}"; do
  p=${pages[$i]}
  name=$(field "$p" 1)
  src="$repo_root/$(field "$p" 4)"
  pager=""
  if ((i > 0)); then
    prev=${pages[$((i - 1))]}
    pager+="<a class=\"prev\" href=\"$(field "$prev" 1).html\"><span>Previous</span>$(field "$prev" 2)</a>"
  fi
  if ((i < count - 1)); then
    next=${pages[$((i + 1))]}
    pager+="<a class=\"next\" href=\"$(field "$next" 1).html\"><span>Next</span>$(field "$next" 2)</a>"
  fi
  args=()
  [[ "$name" != "index" ]] && args+=(--toc --toc-depth=3)
  [[ -f "$here/meta/$name.yaml" ]] && args+=(--metadata-file "$here/meta/$name.yaml")
  [[ -n "$edit" ]] && args+=(--metadata edit-url="$edit/${src#"$repo_root/"}")
  # The docs start with their own "# Title"; the template prints the title.
  sed '/./,$!d' "$src" | sed '1{/^# /d}' | pandoc \
    --from markdown+fenced_divs+bracketed_spans-tex_math_dollars \
    --to html5 \
    --template "$theme/template.html" \
    --lua-filter "$theme/horizon.lua" \
    --metadata-file "$here/site.yaml" \
    --metadata title="$(field "$p" 2)" \
    --metadata source="$name.md" \
    --metadata canonical="$canonical/$([[ "$name" == index ]] || echo "$name.html")" \
    --variable nav="$(nav_for "$name")" \
    --variable pager="$pager" \
    "${args[@]}" \
    --output "$out/$name.html"
  cp "$src" "$out/$name.md"
  { printf '\n\n<!-- %s.md -->\n\n' "$name"; cat "$src"; } >>"$out/llms-full.txt"
done

"$here/redirects.sh" "$out" ..

echo "built $count pages into $out"
