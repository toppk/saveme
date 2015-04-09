#!/bin/bash

# generate a luks key on disk
#
# SECURITY: generate random key material

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

last=$( ls /etc/saveme/keys/luks.cprt-*.key 2> /dev/null| sed  's/.*cprt-\(.*\)\.key$/\1/' | sort -n | tail -1 )

let next="$last + 1"
err=$?
if [ $err -ne 0 ]; then
    echo $last is not numeric
    exit 3
fi

keyf="/etc/saveme/keys/luks.cprt-${next}.key"
echo "# 'keyf':'$keyf'"
# SECURITY: generate random key material
echo dd if=/dev/random of=$keyf bs=1 count=512
echo chmod 600 $keyf
