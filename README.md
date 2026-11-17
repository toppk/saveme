<p align="center"><img src="docs/assets/logo-512.webp" width="128" height="128" alt=""></p>

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
dm-crypt (LUKS). Docs: https://toppk.github.io/saveme/

## Install

saveme runs as root on the system Python (`/usr/bin/python3`, 3.14 or
later, standard library only) and needs bash, plus the tools its scripts
call (btrfs-progs, zfs, cryptsetup, parted). There's nothing to build or
pip-install: a release is a tarball, unpacked as is. Keep the installed copy
root-owned, and don't run it as root from a checkout you can write to.

Layout:

```
/opt/saveme/releases/v<version>/    a release tarball, unpacked
/opt/saveme/current                 -> releases/v<version>
/usr/local/sbin/{snapmgr,disktool,mirroradm}
                                    -> /opt/saveme/current/tools/<tool>
/etc/saveme/                        config, db and keys
```

Install or upgrade, as root, with `saveme-<version>.tar.gz` and `SHA256SUMS`
from the GitHub release:

```
v=0.2.0
sha256sum -c SHA256SUMS
install -d -m 0755 /opt/saveme/releases/v$v
tar -xzf saveme-$v.tar.gz -C /opt/saveme/releases/v$v --strip-components=1 --no-same-owner
chown -R root:root /opt/saveme/releases/v$v && chmod -R go-w /opt/saveme/releases/v$v
ln -sfn releases/v$v /opt/saveme/current
for t in snapmgr disktool mirroradm; do ln -sfn /opt/saveme/current/tools/$t /usr/local/sbin/$t; done
```

The tools find their library and scripts from their own resolved path, so
the symlinks work as is. To roll back, point `current` at the previous
release; old releases stay until you remove them.

## Development

`just check` runs the format, lint and type checks (tools pinned in
`requirements-dev.txt`), and `just test` runs the unit tests, which need no
root and no real disks. CI runs both on Python 3.14. `just dist v<version>`
builds a release tarball and `SHA256SUMS` from a tag into `dist/`.

The docs site is `docs/*.md` rendered with pandoc and the Horizon theme in
`site/`; `just site` builds it into `_site/`, and pushes to `master` publish it
to GitHub Pages.

The system tests in `tests/` (`fullrun.sh <disk>` and friends) run against
real block devices as root and **destroy the disk they're given**. They're
opt-in and never run in CI. `tests/system.sh` checks the tools they drive are
installed and logs their versions.

## Related Links

* http://zfsonlinux.org/faq.html
* https://pthree.org/2012/12/18/zfs-administration-part-xi-compression-and-deduplication/
* https://www.freebsd.org/cgi/man.cgi?zpool%288%29
* http://zfsonlinux.org/faq.html#HowDoIInstallIt
* http://www.evanhoffman.com/evan/2011/10/24/rescan-sata-bus-aka-hot-adding-a-sata-disk-on-a-linux-guest-in-vmware-without-rebooting/
* https://github.com/zfsonlinux/zfs-auto-snapshot/blob/master/src/zfs-auto-snapshot.sh
* http://milek.blogspot.com/2010/03/zfs-diff.html
* https://git-annex.branchable.com/not/
* https://github.com/joeyh/git-annex
* http://www.sentey.com/en/ls-6230-ls-6230/
* https://bup.github.io/
* https://github.com/bup/bup
* https://github.com/bdrewery/zfstools
* https://code.google.com/p/boar/
* http://marc.merlins.org/perso/linux/
* http://marc.merlins.org/perso/btrfs/post_2014-03-21_Btrfs-Tips_-How-To-Setup-Netapp-Style-Snapshots.html
* https://www.mail-archive.com/linux-btrfs@vger.kernel.org/msg05623/btrfs-snap
* https://btrfs.wiki.kernel.org/index.php/SnapBtr
* https://pthree.org/2012/12/19/zfs-administration-part-xii-snapshots-and-clones/
* https://github.com/zfsonlinux/zfs/issues/173
* http://unicolet.blogspot.com/2013/03/a-not-so-short-guide-to-zfs-on-linux.html
* http://wiki.edseek.com/howto:dirvish
* http://www.urbackup.org/
* https://lwn.net/Articles/579009/
* http://confessionsofalinuxpenguin.blogspot.com/2012/09/btrfs-vs-zfsonlinux-how-do-they-compare.html
* https://rudd-o.com/linux-and-free-software/ways-in-which-zfs-is-better-than-btrfs
* https://lwn.net/Articles/342892/
* https://github.com/kdave/btrfsmaintenance
* http://netapp-blog.blogspot.com/2009/12/snapshot-configuration-in-netapp.html
* http://www.la-samhna.de/samhain/s_faq.html
* http://aide.sourceforge.net/
* http://www.ossec.net/
* https://www.tarsnap.com/about.html
* http://www.la-samhna.de/library/scanners.html
