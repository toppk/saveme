# Changelog

## 0.2.1 (2026-11-17)

* Usage errors exit 64 and go to stderr; `help`, `-h` and `--help` print the
  usage and exit 0. Bare `snapmgr` and `disktool` used to exit 12.
* `mirroradm` keeps its database at `/etc/saveme/db/mirror.db` instead of
  `example.db` in the current directory, and exits 1 if that directory is
  missing. Successful commands exit 0 instead of 1.
* `tests/system.sh` checks the tools are installed rather than for 2020
  versions.
* The symlink test runs the tools under the test's Python, so CI covers 3.14.
* `mirroradm`: the `mirrors` table had lost its `blobchksum` column to a
  missing comma; run `mirroradm resetdb` to recreate it. `missing-backup` no
  longer crashes once there are checksums, and `provide-backup` now records a
  backup: `<checksum> <archiveid> <blobchksum> <blobkey> <blobsize>`.
* `mirroradm` uses SQL parameters throughout and closes its connections.
* Removed the unfinished `part-add-ssfs.sh` and the leftover `CommandLine.help()`.

## 0.2.0 (2026-11-13)

Which snapshots `manage` keeps has changed; review your policies before
upgrading.

* Snapshot timestamps' UTC offset was read as seconds; ages and order are now
  right, including across DST changes. The first `manage` after upgrading sees
  every snapshot 4-5 hours younger than before.
* Policy spacing is measured from the last snapshot kept, not the last one
  seen. `1dy-1wk: 8hr` with half-hourly snapshots kept none of them in that
  range in a single run; it now keeps one every 8 hours.
* A spacing of `8hr` keeps a snapshot exactly 8 hours after the last kept one.
* Policy ranges are start-inclusive and end-exclusive. A snapshot on a boundary
  was judged by both ranges and could be deleted twice.
* `manage` skips the delete step when there is nothing to delete.
* Exit codes: 0 success, 1 the generated commands failed, 2 declined at the
  prompt, otherwise the failing script's code. A failed snapshot used to exit 0
  and a successful `manage` 1. Script failures no longer print a traceback.
* `epoch2iso` formats the time it's given, with that date's UTC offset.
* The tools find `lib/` and `scripts/` from their own path, so they work through
  a symlink, and run under `/usr/bin/python3 -I`.
* Python 3.14, standard library only. `setup.py` and nox are replaced by a
  metadata-only `pyproject.toml` and a justfile; install by unpacking a release
  (see README).
* The repository history was rewritten to remove host-specific files; re-clone
  rather than pull into an older clone.

## 0.1.0

* SDLC
* Typing
