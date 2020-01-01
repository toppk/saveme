# saveme

a timeline management tool for filesystems.
<a href="https://pysandra.readthedocs.org/">

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
	      
## Try it out

Please checkout this project, and read the GETTING_STARTED and USAGE docs.  

Requires python3 and bash.

There is more to come...

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
