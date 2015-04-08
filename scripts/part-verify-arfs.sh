#!/bin/bash

# add a ext4 archive fs on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb, mapper/hp1.cfs),
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

if [ "$( lsblk /dev/$part -r  -o fstype,label -n )" != "ext4 $arid" ]; then
    echo "#  FAILURE: $part does not contain expected fstype,label"
    exit 7
fi
echo "#  SUCCESS: $part contains expected fstype,label"
exit 0
