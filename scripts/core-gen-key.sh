#!/bin/bash

# generate a luks key on disk

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

last=$( ls /etc/saveme/keys/luks.hp*key 2> /dev/null| sed  's/.*hp\(.*\).key/\1/' | sort -n | tail -1 )

let next="$last + 1"
keyf="/etc/saveme/keys/luks.hp${next}.key"
echo \# \"key\"==$keyf
echo dd if=/dev/random of=$keyf bs=1 count=512
echo chmod 600 $keyf
