#!/bin/bash


# system binary

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

parted_ver=$( parted  -v | head -1 | sed 's/\.[^.]*$//' )

if [ "$parted_ver" == "parted (GNU parted) 3.2" ]; then
    :
else
    echo unknown parted version $parted_ver
    exit 2
fi


sfdisk_ver=$( sfdisk  --version )

if [ "$sfdisk_ver" == "sfdisk from util-linux 2.34" ]; then
    :
else
    echo unknown sfdisk version $cryptsetup_ver
    exit 3
fi

cryptsetup_ver=$( cryptsetup  --version )

if echo "$cryptsetup_ver" | egrep -q "cryptsetup 2.2.2"; then
    :
else
    echo unknown cryptsetup version $cryptsetup_ver
    exit 4
fi



df_ver=$( df  --version | head -1 )

if [ "$df_ver" == "df (GNU coreutils) 8.31" ]; then
    :
else
    echo unknown df version $df_ver
    exit 5
fi


