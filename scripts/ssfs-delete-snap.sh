#!/bin/bash

# delete snapshot for zfs and btrfs snapshots

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 2 ]; then
   echo "usage: $0 path label # (label can be - for stdin)"
   exit 1
fi
path=$1
label=$2

fstype=$( df $path --output=fstype 2> /dev/null | tail -1 ; exit ${PIPESTATUS[0]})
err=$?
if [ $err -ne 0 ]; then
    echo $path not a directory
    exit 1
fi
labels=""
if [ $label == "-" ]; then
    labels=$(cat)
else
    labels=$label
fi

for label in $labels; do
    if [ $fstype == "zfs" ]; then
	cleanpath=$( echo $path | sed -e 's/^\///'  -e 's/\/$//' )
	if ! zfs list -t snapshot -r $path -o name -H | grep -q  ^$cleanpath\@$label$; then
	    echo snapshot $label does not exist on $path
	    exit 3
	fi
	echo zfs destroy $cleanpath@$label
    elif [[ $fstype == "btrfs"  || $fstype == "-" ]]; then
	if ! btrfs subvolume list -s $path | grep " path .snapshot/" | cut -d\/ -f2- | grep -q ^$label$; then
	    echo snapshot $label does not exist on $path
	    exit 3
	fi
	cleanpath=$( echo $path | sed   -e 's/\/$//' )
	echo btrfs subvolume delete $cleanpath/.snapshot/$label
    else
	echo not btr or zed
	exit 2
    fi
done
