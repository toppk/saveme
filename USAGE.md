```bash
[root@static tests]# ../tools/snapmgr create /t2/home 

PLEASE CONFIRM THE FOLLOWING ACTION
---
# 'snap':'20150402_02:39:31_-0400'
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:31_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Create a readonly snapshot of '/t2/home' in '/t2/home/.snapshot/20150402_02:39:31_-0400'
---
[root@static tests]# ../scripts/
core-gen-arid.sh      disk-add-part.sh      part-add-arfs.sh      part-add-ssfs.sh      ssfs-delete-snap.sh~  ssfs-take-snap.sh     sys-detach-arfs.sh
core-gen-key.sh       disk-rem-part.sh      part-add-luks.sh      ssfs-delete-snap.sh   ssfs-list-snap.sh     sys-attach-arfs.sh    
[root@static tests]# ../scripts/ssfs-
ssfs-delete-snap.sh   ssfs-delete-snap.sh~  ssfs-list-snap.sh     ssfs-take-snap.sh     
[root@static tests]# ../scripts/ssfs-take-snap.sh 
usage: ../scripts/ssfs-take-snap.sh path [--label=XXX]
[root@static tests]# ../scripts/ssfs-take-snap.sh /t2/home
# 'snap':'20150402_02:39:51_-0400'
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:51_-0400
[root@static tests]# echo $?
0

```
