#!/bin/bash

# lowlevel disk,part,cprt,arfs teardown
#
# not quality

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 4 ]; then
    echo usage: $0 arid cprt keyf disk
    exit 1
fi

if ! test -f lowlevel-teardown.sh; then
    echo you must be in tests directory $0
    exit 2
fi

arid=$1
cprt=$2
keyf=$3
disk=$4

testname=${testname:-lowlevel-teardown}
. lib.sh

# == STEP 1 - unmount archive filesystem ==
runme "lowlevel-teardown_sys-detach-arfs_$arid" ../scripts/sys-detach-arfs.sh  $arid || exit

#what should work


# == STEP 2 - close luksDevice
cpid=$( basename $cprt )
systemctl stop systemd-cryptsetup@${cpid}.service

sed -i.bak '/^'$cpid'[ \t]/d' /etc/crypttab
systemctl daemon-reload

# this is good enough
mv $keyf $keyf.OLD

dd if=/dev/zero of=/dev/$disk bs=1024k count=100 conv=fdatasync,notrunc > /dev/null 2> /dev/null

