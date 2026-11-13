#
# cfg - all configuration settings.  no intradepenencies,
#       so only depends on pathlib
#

from pathlib import Path

SETTINGS = {
    "default-snapshot-policy": "0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none",
    "snapshot-pattern": r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d[-+]\d\d\d\d$",
    "scripts-directory": str(Path(__file__).resolve().parents[2] / "scripts"),
    "database-directory": "/etc/saveme/db",
}


def getsnapshotpattern() -> str:
    assert isinstance(SETTINGS["snapshot-pattern"], str)
    return SETTINGS["snapshot-pattern"]


def getdefsnappol() -> str:
    assert isinstance(SETTINGS["default-snapshot-policy"], str)
    return SETTINGS["default-snapshot-policy"]


def getdbdir() -> str:
    assert isinstance(SETTINGS["database-directory"], str)
    return SETTINGS["database-directory"]


def getscriptsdir() -> str:
    assert isinstance(SETTINGS["scripts-directory"], str)
    return SETTINGS["scripts-directory"]
