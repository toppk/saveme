#!/bin/bash

# add a ext4 archive fs on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb, mapper/cprt-1),
#             id (label and mount point, must be unique and simple. hint: use core-gen-arid.sh)

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 arid
   exit 1
fi
   
arid=$1

if [ $( df --output /arfs/$arid | tail -1 | awk '{ print $2 }' ) != "ext4" ]; then
    echo "#  FAILURE: /arfs/$arid is not as expected"
    exit 8
fi
echo "#  SUCCESS: /arfs/$arid is and ext4 mounted filesystem"
exit 0
