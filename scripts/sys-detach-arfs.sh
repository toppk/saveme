#!/bin/bash

# add a ext4 archive fs on a partition
# parameters: id (label and mount point, must be unique and simple. hint: use core-gen-arid.sh)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 arid
   exit 1
fi
   
arid=$1

if ! test -b /dev/disk/by-label/$arid; then
    echo LABEL=$arid is not a block device
    exit 4
fi

if ! systemctl status arfs-$arid.automount | egrep -q 'active \((running|waiting)\)'; then
    echo \# notice: $arid is not running
else
    echo systemctl stop arfs-$arid.automount
fi
if ! test -d /arfs/$arid; then
    echo \# notice: /arfs/$arid does not exist
else
    echo rmdir /arfs/$arid
fi
if ! grep -q '^LABEL='$arid'[ \t]' /etc/fstab; then
    echo \# notice: LABEL=$arid fstab entry not found
else
    echo sed -i.bak "'/^LABEL=$arid[ \t]/d' /etc/fstab"
    echo systemctl daemon-reload
fi
