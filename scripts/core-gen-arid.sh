#!/bin/bash

# generate a archivefs id

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

last=$( awk '$2 ~ /^\/alt\/xp/ { print substr($2,8) }' /etc/fstab | sort -n | tail -1 )

let next="$last + 1"

arid="xp${next}"

match=$( cat /etc/fstab | awk '$1 ~ /^LABEL='$arid'$/ { print $0 }' )
if [ ! -z "$match" ]; then
    echo $arid has a match
    exit 2
fi

echo \# \"arid\"==$arid

