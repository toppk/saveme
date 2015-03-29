#!/bin/bash

# add a ext4 archive fs on a partition
# parameters: id (must exist and be ext4)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 arid
   exit 1
fi
   
arid=$1

if ! test -b /dev/disk/by-label/$arid; then
    echo $part is not a block device
    exit 4
fi

fstype=$( lsblk $( blkid -L $arid ) -o fstype -n )
if [ "$fstype" != "ext4" ]; then
    echo $fstype is not ext4
    exit 6
fi

# unique
fsln=$( cat /etc/fstab | awk '$1 ~ /^LABEL='$arid'$/ { print $0 }' )
if [ "$fsln" != "" ]; then
    echo $arid is already there
    if ! systemctl status alt-$arid.automount | egrep -q 'active \((running|waiting)\)'; then
	echo also, $arid is not running to fix, run:
	printf "\tsystemctl  start   alt-${arid}.automount\n"
	
    fi
    exit 5
fi



echo echo "'"'LABEL='$arid' /alt/'$arid'                   ext4    noauto,comment=systemd.automount        1 4'"'"' >> /etc/fstab'  
echo systemctl  daemon-reload
echo systemctl  start   alt-${arid}.automount
