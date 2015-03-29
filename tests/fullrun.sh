#!/bin/bash

# full cycle disk -> arfs -> disk
export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if ! test -f fullrun.sh; then
    echo you must be in tests directory [$0]
    exit 2
fi

testname=${testname:-fullrun}
. lowlevel.sh sdo
. lowlevel-teardown.sh  xp5 mapper/hp35.cfs /etc/saveme/keys/luks.hp35.cfs.key sdo
echo "#  notice: logs are $logdir"
