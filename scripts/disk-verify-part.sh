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


if ! lsblk /dev/$disk -n -o type | grep -q part; then
    echo "#  FAILURE: $disk does not have a partition type"
    exit 3
fi
echo "#  SUCCESS: $disk has a partition type"
