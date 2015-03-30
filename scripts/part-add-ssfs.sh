#!/bin/bash

# add a snapshoting fs on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb, mapper/hp1.cfs),
#             id (label and mount point, must be unique and simple. hint: use core-gen-ssid.sh)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 2 ]; then
   echo usage: $0 part ssid
   exit 1
fi
   
part=$1
ssid=$2

if ! test -b /dev/$part; then
    echo $part is not a block device
    exit 4
fi

type=$( lsblk -P -o name,type,fstype /dev/$part | head -1 )

if ! echo $type | egrep -q 'TYPE="(part|crypt)"'; then
    echo $part is not a part or crypt
    exit 2
fi

if ! echo $type | grep -q 'FSTYPE=""'; then
    echo $part has a fstype
    exit 3
fi


# unique
fsln=$( cat /etc/fstab | awk '$1 ~ /^LABEL='$arid'$/ { print $0 }' )
if [ "$fsln" != "" ]; then
    echo $arid is not unique
    exit 5
fi

# simple
pass=$( echo $arid |  grep '^[[:alpha:]][[:alnum:]]*$' )

if [ "$pass" == "" ]; then
    echo $arid does not match expected pattern
    exit 6
fi

exit 3

# zfs
zpool create  t3 mirror /dev/mapper/hp35.cfs /dev/mapper/hp34.cfs
zfs create t3/home
zfs set compression=lz4 t3/home
zfs snapshot t3/home@$( date '+%Y%m%d_%H:%M:%S_%z' )
zfs set snapdir=visible t3/home
zfs list -t snapshot
# btrfs
mkfs.btrfs -L t2 -m raid1 -d raid1 /dev/mapper/hp30.cfs /dev/mapper/hp31.cfs
mount  LABEL=t2   /t2
btrfs subvol  create /t2/home
mkdir /t2/home/.snapshot
btrfs subvol snapshot /t2/home /t2/home/.snapshot/$( date '+%Y%m%d_%H:%M:%S_%z' )
btrfs subvolume list -s /t2



