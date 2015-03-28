#!/bin/bash


# system binary

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

parted_ver=$( parted  -v | head -1 )

if [ "$parted_ver" == "parted (GNU parted) 3.2" ]; then
    :
else
    echo unknown parted version $parted_ver
    exit 2
fi


sfdisk_ver=$( sfdisk  --version )

if [ "$sfdisk_ver" == "sfdisk from util-linux 2.25.2" ]; then
    :
else
    echo unknown sfdisk version $cryptsetup_ver
    exit 3
fi

cryptsetup_ver=$( cryptsetup  --version )

if [ "$cryptsetup_ver" == "cryptsetup 1.6.6" ]; then
    :
else
    echo unknown cryptsetup version $cryptsetup_ver
    exit 4
fi




