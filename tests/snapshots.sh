#!/bin/bash

# snapshot manage create tests

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


# == STEP 1 -  ==
runme "snapshots_manage" ../tools/snapmgr || exit

