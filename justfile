# Run `just` to list recipes.

src := "lib tests tools/snapmgr tools/disktool tools/mirroradm"

default:
    @just --list --unsorted

# Format, lint and type checks (tools from requirements-dev.txt); CI runs this.
check:
    black --check --diff {{src}}
    isort --check --diff {{src}}
    flake8 {{src}}
    mypy lib/saveme

# Unit tests; no root or real disks needed.
test:
    python3 -I tests/python.py -v

# Reformat in place.
fmt:
    isort {{src}}
    black {{src}}

# Build dist/saveme-<version>.tar.gz and SHA256SUMS from a tag, e.g. `just dist v0.2.0`.
dist tag:
    #!/usr/bin/env bash
    set -euo pipefail
    v="{{tag}}"; v="${v#v}"
    git show "{{tag}}:pyproject.toml" | grep -qx "version = \"$v\"" || { echo "pyproject.toml at {{tag}} isn't $v" >&2; exit 1; }
    mkdir -p dist
    git archive --format=tar.gz --prefix="saveme-$v/" -o "dist/saveme-$v.tar.gz" "{{tag}}"
    cd dist && sha256sum "saveme-$v.tar.gz" > SHA256SUMS && cat SHA256SUMS
