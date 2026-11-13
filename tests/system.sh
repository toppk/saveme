#!/bin/bash

# check the system tools the scripts drive are present, and log their versions

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

status=0
for tool in parted sfdisk cryptsetup df btrfs; do
    if ! command -v "$tool" >/dev/null; then
        echo "missing $tool"
        status=2
        continue
    fi
    echo "$tool: $( "$tool" --version 2>&1 | head -1 )"
done
exit $status
