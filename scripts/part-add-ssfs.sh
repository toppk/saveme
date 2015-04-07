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

## not ready for prime time
exit 3


# zfs
echo zpool create  t3 mirror /dev/mapper/hp35.cfs /dev/mapper/hp34.cfs
echo zfs create t3/home
echo zfs set compression=lz4 t3/home
echo zfs snapshot t3/home@$( date '+%Y-%m-%dT%H:%M:%S%z' )
echo zfs set snapdir=visible t3/home
# btrfs
echo mkfs.btrfs -L t2 -m raid1 -d raid1 /dev/mapper/hp30.cfs /dev/mapper/hp31.cfs
echo mount  LABEL=t2   /t2
echo btrfs subvol  create /t2/home


