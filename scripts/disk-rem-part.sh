#!/bin/bash

# remove a gpt partition table from a disk
# parameter: disk (don't include /dev/ just, e.g.: sdb)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 disk
   exit 1
fi
   
disk=$1

if ! test -b /dev/$disk; then
    echo $disk is not a block device
    exit 4
fi

type=$( lsblk -n /dev/$disk --output type )

if ! echo $type | grep -q disk; then
    echo $disk is not a disk
    exit 2
fi

sfdisk -R /dev/$disk
err=$?
if [ $err -ne 0 ];then
    echo $disk is busy
    exit 3
fi

echo dd if=/dev/zero of=/dev/$disk bs=1024k count=100
