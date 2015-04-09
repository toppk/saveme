#!/bin/bash

# add a ext4 archive fs on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb, mapper/cprt-1),
#             id (label and mount point, must be unique and simple. hint: use core-gen-arid.sh)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 2 ]; then
   echo usage: $0 part arid
   exit 1
fi
   
part=$1
arid=$2

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


echo mke2fs -T ext4,largefile  -L $arid -j -m 1  -O sparse_super,dir_index -J size=128 /dev/$part
