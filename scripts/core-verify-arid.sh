#!/bin/bash

# verify a archivefs id is not in use

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 arid
   exit 1
fi
   
part=$1

match=$( cat /etc/fstab | awk '$1 ~ /LABEL='$arid'$/ { print $0 }' )
if [ ! -z "$match" ]; then
    echo "#  FAILURE: $arid has a match in fstab"
    exit 2
fi

if [ -d /arfs/$arid ]; then
    echo "#  FAILURE: $arid has a directory in /arfs"
    exit 3
fi

echo "#  SUCCESS: $arid is not in use"
