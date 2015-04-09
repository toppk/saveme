#!/bin/bash

# get filesystem capacity

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 path
   exit 1
fi
   
path=$1

if [ ! -d $path ]; then
    echo "#  FAILURE: $path does not exist"
    exit 3
fi

capacity=$( df --output=avail $path  --block-size=1 | tail -1; exit ${PIPESTATUS[0]} )
err=$?
if [ $err != 0 ]; then
    echo "#  FAILURE:  running df $err"
    exit 2
fi

echo "# 'capacity':'$capacity'"
