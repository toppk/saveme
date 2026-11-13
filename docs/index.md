# saveme

Snapshots and encrypted archive disks for Linux, on btrfs, zfs and LUKS.

## What it does

* **`snapmgr`** takes btrfs and zfs snapshots and thins them by age. A policy
  like `0-1dy: all, 1dy-1wk: 4hr, 1wk-8wk: 1wk, 8wk+: none` says how dense
  history should be at each age, however often snapshots are taken. Snapshot
  names are their timestamps, so there's no other state to keep in sync.
* **`disktool`** prepares archive disks: a GPT partition, LUKS encryption with
  a generated key in `/etc/saveme/keys/`, and an ext4 filesystem mounted under
  `/arfs/<id>`.
* **`mirroradm`** is unfinished: it indexes and checksums files into SQLite,
  toward backups made from snapshots rather than the live filesystem.

saveme doesn't encrypt snapshots; encryption applies to the LUKS archive disks
it prepares. Snapshots catch mistakes, but they're not a backup by themselves.

## How it runs

Every root action, snapshot creation and deletion included, is a short bash
script in `scripts/` that checks its inputs and prints the commands it would
run. saveme shows that list and asks before running it, unless `--noprompt` is
given. So the commands that change disks are always visible, at the prompt and
in the log.

```
# crontab -l
10,40 * * * * snapmgr create /my/vol --noprompt
0     4 * * * snapmgr manage /my/vol --noprompt \
                  --policy="0-1dy: all, 1dy-1wk: 8hr, 1wk-1yr: 2wk, 1yr+: none"
```

It runs on Linux with btrfs, zfs, ext4, GPT partition tables and
dm-crypt (LUKS). See Usage for details.
