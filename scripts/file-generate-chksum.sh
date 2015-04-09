#!/bin/bash

# generate a checksum
# parameters: filepath
# SECURITY: hash is selected

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
   echo usage: $0 filepath
   exit 1
fi
   
filepath=$1

if ! test -r $filepath; then
    echo cannot read $filepath
    exit 2
fi

echo sha512:$( sha512sum $filepath | awk '{ print $1 }' )+$( stat -c%s $filepath )
