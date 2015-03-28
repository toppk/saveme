#!/bin/bash

# add a luks layer on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb),
#             key (path to secure keyfile, must match pattern. hint: use core-gen-key.sh)
# SECURITY: cipher, size, hash are selected.

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 2 ]; then
   echo usage: $0 part key
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
cprt=$( basename $keyf | sed 's/^luks.\(.*\).key$/\1/' )

if [ "$cprt" == "" ]; then
    echo $keyf does not match expected pattern
    exit 6
fi

# SECURITY: cipher size hash
## found off google searches.  we should get some confirmation and include references.
echo "# 'cryptpart':'mapper/$cprt'"
echo cryptsetup --verbose -c aes-xts-plain64 -s 256 -h sha512 luksFormat /dev/$part $keyf  -q
#echo cryptsetup --key-file $keyf luksOpen /dev/$part $cprt # systemd does this
echo echo $cprt' /dev/disk/by-uuid/$( lsblk -n /dev/'$part' -o uuid,type -r | grep part | awk '\''{ print $1 }'\'' ) '$keyf' >> /etc/crypttab'
echo systemctl daemon-reload
echo systemctl systemd-cryptsetup@${cptr}.service
