#!/bin/bash

# add a gpt partition table to a disk
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

if echo $type | grep -q part; then
    echo $disk has partitions or is not a disk
    exit 2
fi

sfdisk -R /dev/$disk
err=$?
if [ $err -ne 0 ];then
    echo $disk is busy
    exit 3
fi

echo parted /dev/$disk mktable gpt
echo parted -a optimal /dev/$disk mkpart primary 0% 100%
