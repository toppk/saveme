#!/bin/bash

# add a luks layer on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb),
#             keyf (path to secure keyfile, must match pattern. hint: use core-gen-key.sh)
# SECURITY: cipher, size, hash are selected.

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 2 ]; then
   echo usage: $0 part keyf
   exit 1
fi
   
part=$1
keyf=$2

if ! test -b /dev/$part; then
    echo $part is not a block device
    exit 4
fi

type=$( lsblk -P -o name,type,fstype /dev/$part | head -1 )

if ! echo $type | grep -q 'TYPE="part"'; then
    echo $part is not a part
    exit 2
fi

if ! echo $type | grep -q 'FSTYPE=""'; then
    echo $part has a fstype
    exit 3
fi

if ! test -f "$keyf"; then
    echo $keyf is not a file
    exit 5
fi

# pattern
cpid=$( basename $keyf | sed 's/^luks.\(.*\).key$/\1/' )

if [ "$cpid" == "" ]; then
    echo $keyf does not match expected pattern
    exit 6
fi

secsize=$( cd -P /sys/class/block/$part/..  && cat queue/hw_sector_size )
if [[ "$secsize" != 512 && "$secsize" != 4096 ]]; then
   echo $part has unknown sector size [$secsize]
   exit 7
fi


ecpi=$( systemd-escape $cpid | sed 's/\\/\\\\/g' )
uuid=$( uuidgen )
# SECURITY: cipher size hash
## found off google searches.  we should get some confirmation and include references.
## https://crypto.stackexchange.com/questions/48935/why-use-argon2i-or-argon2d-if-argon2id-exists
## https://cloudnull.io/2017/05/issuing-allowing-discards-enabling-timers-oh-my-2/
#  --persistent --allow-discards ???
echo "# 'cprt':'mapper/$cpid'"
echo "# 'ecpi':'$ecpi'"
echo "# 'uuid':'$uuid'"
echo cryptsetup -c aes-xts-plain64 -s 512 -h sha512 --sector-size=$secsize --pbkdf=argon2id --uuid=$uuid --type=luks2 luksFormat /dev/$part $keyf  -q
echo udevadm settle
echo echo $cpid /dev/disk/by-uuid/$uuid  $keyf '>>' /etc/crypttab
echo systemctl daemon-reload
#echo cryptsetup --key-file $keyf luksOpen /dev/$part mapper/$cpid # systemd does this
echo systemctl start systemd-cryptsetup@${ecpi}.service
