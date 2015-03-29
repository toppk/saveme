#!/bin/bash

# full cycle disk -> arfs -> disk
export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if ! test -f fullrun.sh; then
    echo you must be in tests directory [$0]
    exit 2
fi

if [ $# -ne 1 ]; then
    echo usage: $0 disk
    exit 1
fi

disk=$1

testname=${testname:-fullrun}
echo "#  RUNNING: lowlevel.sh $disk"
. lowlevel.sh $disk
echo "#  RUNNING: lowlevel-teardown.sh $arid $cprt $keyf $disk"
. lowlevel-teardown.sh  $arid $cprt $keyf $disk
echo "#  SUCCESS: finished fullrun.sh $disk"
echo "#   notice: logs are $logdir"
