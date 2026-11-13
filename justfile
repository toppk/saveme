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
