#!/bin/bash

# add a luks layer on a partition
# parameters: part (don't include /dev/ just, e.g.: sdb),
#             keyf (path to secure keyfile, must match pattern. hint: use core-gen-key.sh)
# SECURITY: cipher, size, hash are selected.

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 part
   exit 1
fi
   
part=$1

if ! test -b /dev/$part; then
    echo "#  FAILURE: $part is not a block device"
    exit 4
fi

if [ `lsblk /dev/$part  -o type -n` != "crypt" ]; then
    echo "#  FAILURE: $cryptpart is not crypt partition"
    exit 5
fi
echo "#  SUCCESS: $part is crypt"

