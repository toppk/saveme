# Usage Guide

## Lowlevel


## Snapshots

### Creating Snapshots


```bash
[root@static tests]# ../tools/snapmgr create /t2/home 

PLEASE CONFIRM THE FOLLOWING ACTION
---
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:31_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Create a readonly snapshot of '/t2/home' in '/t2/home/.snapshot/20150402_02:39:31_-0400'
---
[root@static tests]# ../scripts/ssfs-take-snap.sh 
usage: ../scripts/ssfs-take-snap.sh path [--label=XXX]
[root@static tests]# ../scripts/ssfs-take-snap.sh /t2/home
# 'snap':'20150402_02:39:51_-0400'
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:51_-0400
[root@static tests]# echo $?
0
```
