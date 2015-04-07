#!/bin/bash

#

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ge 1 ]; then
    path=$1
fi


if [ $# -eq 2 ]; then
    if [ "${2:0:8}" == "--label=" ]; then
	label="${2:8}"
    else
	echo usage: $0 path [--label=XXX]
	exit 2
    fi
fi

if [ -z "$path" ]; then
   echo usage: $0 path [--label=XXX]
   exit 1
fi

if [ -z "$label" ]; then
    label=$( date '+%Y-%m-%dT%H:%M:%S%z' )
fi


fstype=$( df $path --output=fstype 2> /dev/null | tail -1 ; exit ${PIPESTATUS[0]})
err=$?
if [ $err -ne 0 ]; then
    echo $path not a directory
    exit 1
fi


if [ $fstype == "zfs" ]; then
    cleanpath=$( echo $path | sed -e 's/^\///'  -e 's/\/$//' )
    if zfs list -t snapshot -r $path -o name -H | grep -q  ^$cleanpath\@$label$; then
	echo snapshot $label exists on $path
	exit 3
    fi
	
    echo "# 'snap':'$label'"
    echo zfs snapshot $cleanpath@$label
elif [[ $fstype == "btrfs"  || $fstype == "-" ]]; then
    if btrfs subvolume list -s $path | grep " path .snapshot/" | cut -d\/ -f2- | grep -q ^$label$; then
	echo snapshot $label exists on $path
	exit 3
    fi
    
    cleanpath=$( echo $path | sed   -e 's/\/$//' )
    echo "# 'snap':'$label'"
    test -d $cleanpath/.snapshot || echo mkdir $cleanpath/.snapshot
    echo btrfs subvolume snapshot -r $cleanpath $cleanpath/.snapshot/$label
else
    echo not btr or zed
    exit 2
fi
    
