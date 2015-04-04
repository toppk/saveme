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

path=$1

# == STEP 1 - help  ==
runme "snapshots_help" ../tools/snapmgr && exit
echo "# this was supposed to fail"
# == STEP 2 - create  ==
launch "snapshots_create" ../tools/snapmgr create $path --noprompt || exit
echo "# Success"


