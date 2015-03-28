#!/bin/bash


# lowlevel disk,part,cprt,arfs tests

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '


if [ $# -ne 1 ]; then
    echo usage: $0 disk
    exit 1
fi

if [ $0 != "./lowlevel.sh" ]; then
    echo you must be in tests directory
    exit 2
fi

. ./lib.sh

disk=$1


runme --sleep "lowlevel_disk-add-part_$disk" ../scripts/disk-add-part.sh $disk || exit

#what should work
if ! lsblk /dev/$disk -n -o type | grep -q part; then
    echo "#  FAILURE: $disk does not have a partition type"
    exit 3
fi
echo '#  SUCCESS: $disk has a partition type"

key=""
runme "lowlevel_core-gen-key" ../scripts/core-gen-key.sh || exit

#what should work
if [ ! -f $key ]; then
    echo "#  FAILURE: $keyf is not a file"
    exit 4
fi
echo "#  SUCCESS: core-gen-key"

part="${disk}1"
cleankeyf=$( echo $keyf | tr '/' '+' )

cryptpart=""
runme "lowlevel_part-add-luks_$part_$cleankeyf" ../scripts/part-add-luks.sh $part $keyf || exit
cryptpart

