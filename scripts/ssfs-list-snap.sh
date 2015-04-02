#!/bin/bash

#

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '


if [ $# -ne 1 ]; then
   echo usage: $0 path
   exit 1
fi
   
path=$1

fstype=$( df $path --output=fstype 2> /dev/null | tail -1 ; exit ${PIPESTATUS[0]})
err=$?
if [ $err -ne 0 ]; then
    echo $path not a directory
    exit 1
fi


if [ $fstype == "zfs" ]; then
    cleanpath=$( echo $path | sed -e 's/^\///'  -e 's/\/$//' )
    zfs list -t snapshot -r $path -o name -H | grep  ^$cleanpath\@ | cut -d\@ -f2
elif [[ $fstype == "btrfs"  || $fstype == "-" ]]; then
    btrfs subvolume list -s $path | grep " path .snapshot/" | cut -d\/ -f2-
else
    echo not btr or zed
    exit 2
fi
    
