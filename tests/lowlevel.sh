#!/bin/bash


# lowlevel disk,part,cprt,arfs tests

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
    echo usage: $0 disk
    exit 1
fi

if ! test -f lowlevel.sh; then
    echo you must be in tests directory $0
    exit 2
fi

testname=${testname:-lowlevel}
. lib.sh


# == STEP 1 - create partition table with first partition ==
disk=$1
runme --sleep "lowlevel_disk-add-part_$disk" ../scripts/disk-add-part.sh $disk || exit
#what should work
# 1 failure here after 192 runs..
launch "lowlevel_disk-verify-part_$" ../scripts/disk-verify-part.sh $disk || exit

# == STEP 2 - generate key ==
keyf=""
runme "lowlevel_core-gen-key" ../scripts/core-gen-key.sh || exit

#what should work
if [ ! -f $keyf ]; then
    echo "#  FAILURE: $keyf is not a file"
    exit 4
fi
echo "#  SUCCESS: core-gen-key"

# == STEP 3 - create encrypted partition on disk partition ==
part="${disk}1"
cleankeyf=$( echo $keyf | tr '/' '+' )
cprt=""
runme "lowlevel_part-add-luks_$part_$cleankeyf" ../scripts/part-add-luks.sh $part $keyf || exit

#what should work
if [ `lsblk /dev/$cprt  -o type -n` != "crypt" ]; then
    echo "  FAILURE: $cryptpart is not crypt partition"
    exit 5
fi
echo "#  SUCCESS: $cprt is crypt"

# == STEP 4 - generate archive filesystem id ==
arid=""
runme "lowlevel_core-get-arid" ../scripts/core-gen-arid.sh || exit

#what should work
if [ -z "$arid" ]; then
    echo "  FAILURE: did not generate arid"
    exit 6
fi
echo "#  SUCCESS: arid is $arid"

# == STEP 5 - create archive filesystem on encrypted partition ==
cleancprt=$( echo $cprt | tr '/' '+' )
runme "lowlevel_part-add-arfs_${cleancprt}_$arid" ../scripts/part-add-arfs.sh $cprt $arid || exit
## workaround: need time to settle?
seq 10 | while read a; do lsblk /dev/$cprt -o fstype -r -n | grep -q ext4 && break || echo "#  notice: sleeping for 50ms waiting for drive";usleep 50000;done
#what should work
if [ "$( lsblk /dev/$cprt -r  -o fstype,label -n )" != "ext4 $arid" ]; then
    echo "#  FAILURE: $cprt does not contain expected fstype,label"
    exit 7
fi
echo "#  SUCCESS: $cprt contains expected fstype,label"

# == STEP 6 - mount archive filesystem ==
runme "lowlevel_sys-attach-arfs_$arid" ../scripts/sys-attach-arfs.sh  $arid || exit

#what should work
if [ $( df --output /arfs/$arid | tail -1 | awk '{ print $2 }' ) != "ext4" ]; then
    echo "#  FAILURE: $cprt does not contain expected fstype,label"
    exit 8
fi
echo "#  SUCCESS: /arfs/$arid is and ext4 mounted filesystem"

for key in arid cprt disk keyf part; do
    echo "# '$key':'$( eval echo \$$key)'"
done

