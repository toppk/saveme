# saveme

a timeline management tool for filesystems.

## Introduction

Protecting ones data has always been a tough challenge. Fortunetly there
has been a lot of new technology developed that give new ways to solve
old problems.  Here are tools that enable people to manage and protect
their data, in a better way.

This tool will help you manage your filesystems, including snapshots
with a simpler more flexible policy format.  We're also building
backups based on indexing and checksum'ing files from the snapshot.
There are several design advantages that one gets when backing up the
snapshot vs the live filesystem, but the backup functionality can be
used without snapshots as well.

## Compatability

This tool is designed to be ported to any storage technology.
Currently works with:

* linux
* btrfs
* zfs
* ext4
* gpt partition tables
* dm-crypt (luks/cryptsetup) for crypto

## Status

* General - This software is still experimental.  Not everthing
            works, but the scripts and execution follow a simple
            design, that anyone who feels comfortable running
            commands as root that can reformat filesystem should
            be able to review any command simply.

* Lowlevel - There are scripts to assist setting up partitions
             setting up crypto block devices, adding filesystems to
	     partitions.  All disk level commands are contained in
             shell scripts that average less then 40 lines per file.
             There is a tool to help run through all the steps to
             create a new filesystem on a new disk.

See USAGE for more details.

* Snapshots - There is a tool to manage snapshots with a simple policy.
              Gone are the hourly/daily concepts, and replaced with a
	      unified policy regarding snapshot density.

```
# crontab -l
10,40 * * * * snapmgr create /my/vol --noprompt
0     4 * * * snapmgr manage /my/vol --policy="0-1dy: all, 1dy-1wk: 8hr, \
                                               4wk-1yr: 2wk, 1yr+: none" --noprompt
#

```
See USAGE for more details.

* Backups - This tool is currently in progress.  Currently there is a
            sqlite database that stores indexes and checksums of files.
            There will be more support code to place each file on a
            set of fileystems registerd as "archive" where each file
            will be encrypted with it's own key.

See lib/saveme/mirror.py for details.
