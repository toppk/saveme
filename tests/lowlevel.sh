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

disk=$1

# init
echo \# STARTING: disk-add-part
../scripts/disk-add-part.sh $disk > lowlevel_disk-add-part_$disk.out 2> lowlevel_disk-add-part_$disk.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: disk-add-part retval=$err
    more lowlevel_disk-add-part_$disk.out lowlevel_disk-add-part_$disk.err | cat
    exit 3
fi

# last chance
echo \# WARNING: I AM ABOUT TO DESTROY /dev/$disk!!!!!
echo \# notice: waiting for ten seconds
sleep 10

# run
echo \# RUNNING: disk-add-part
bash -e lowlevel_disk-add-part_$disk.out > lowlevel_disk-add-part_RUN.out 2> lowlevel_disk-add-part_RUN.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: during run of lowlevel_disk-add-part_$disk.out
    exit 6
fi

#what should work
if ! lsblk /dev/$disk -n -o type | grep -q part; then
    echo \# FAILURE: $disk does not have a partition type
    exit 4
fi
echo \# SUCCESS: $disk has a partition type

#init 
echo \# STARTING: core-gen-key
../scripts/core-gen-key.sh > lowlevel_core-gen-key.out 2> lowlevel_core-gen-key.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: core-gen-key retval=$err
    more lowlevel_core-gen-key.out lowlevel_core-gen-key.err | cat
    exit 3
fi
#run
echo \# RUNNING: core-gen-key
bash -e lowlevel_core-gen-key.out > lowlevel_core-gen-key_RUN.out 2> lowlevel_core-gen-key_RUN.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: during run of lowlevel_disk-add-part_$disk.out
    exit 7
fi
keyf=$( cat lowlevel_core-gen-key.out | sed -n  "/^#/s/.*'key':'\(.*\)'$/\1/p" )
if [ ! -f $keyf ]; then
    echo \# FAILURE: $keyf is not a file
    exit 8
fi
echo \# SUCCESS: core-gen-key

part="${disk}1"
cleankeyf=$( echo $keyf | tr '/' '+' )

echo \# STARTING: part-add-luks
../scripts/part-add-luks.sh $part $keyf  > lowlevel_part-add-luks_${part}_${cleankeyf}.out 2> lowlevel_part-add-luks_${part}_${cleankeyf}.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: part-add-luks retval=$err
    more lowlevel_part-add-luks_${part}_${cleankeyf}.out lowlevel_part-add-luks_${part}_${cleankeyf}.err | cat
    exit 3
fi
echo \# RUNNING: part-add-luks
bash -e lowlevel_part-add-luks_${part}_${cleankeyf}.out > lowlevel_part-add-luks_${part}_${cleankeyf}_RUN.out 2> lowlevel_part-add-luks_${part}_${cleankeyf}_RUN.err
err=$?
if [ $err -ne 0 ]; then
    echo \# FAILURE: during run of lowlevel_disk-add-part_$disk.out
    exit 7
fi
keyf=$( cat lowlevel_core-gen-key.out | sed -n  "/^#/s/.*'key':'\(.*\)'$/\1/p" )
if [ ! -f $keyf ]; then
    echo \# FAILURE: $keyf is not a file
    exit 8
fi
echo \# SUCCESS: core-gen-key

