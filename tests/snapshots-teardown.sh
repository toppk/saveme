#!/bin/bash

# snapshot cleanup script
# WARNING: this will delete all snapshots

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
    echo usage: $0 path
    exit 1
fi

if ! test -f snapshots.sh; then
    echo you must be in tests directory $0
    exit 2
fi

testname=${testname:-snapshots}
. lib.sh

path=$1

# == STEP 1 - help  ==
output=$( ../tools/snapmgr list $path )
err=$?
if [ $err -ne 0 ]; then
    echo snapshot list failed $err [[ $output ]]
    exit 2
fi
if [ -z "$output" ] ; then
     echo you do not have snapshots [[ $output ]]
     exit 1
fi
# == STEP 2 - delete  ==
../tools/snapmgr manage $path --policy="0+: none"

