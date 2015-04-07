#!/bin/bash

# snapshot manage create tests

export PATH=/bin:/sbin
PS4='+\D{%s} [$?] # '

if [ $# -ne 1 ]; then
    echo usage: $0 path
    exit 1
fi

if ! test -f snapshots.sh; then
    echo you must be in tests directory $0
    exit 2
fi

testname=${testname:-snapshots}
. lib.sh

path=$1

# == STEP 1 - help  ==
output=$( ../tools/snapmgr list $path )
err=$?
if [ $err -ne 0 ]; then
    echo snapshot list failed $err [[ $output ]]
    exit 2
fi
if [ ! -z "$output" ] ; then
     echo you have snapshots [[ $output ]]
     exit 1
fi
echo "# this was supposed to fail"
# == STEP 2 - create  ==

outdir="$path/saveme.testdir"
if [ -d $outdir ]; then
    echo removing directory $outdir
    rm -rf $outdir
fi

now=$( date +%s )
let oneweek0hr="$now - 7 * 24 * 60 * 60"
let oneweek1hr="$oneweek0hr - 60 * 60"
let oneweek2hr="$oneweek1hr - 60 * 60"
let now1hr="$now - 60 * 60"
let now2hr="$now1hr - 60 * 60"
let now3hr="$now2hr - 60 * 60"

mkdir $outdir
echo content1 > $outdir/before.1
echo content2 > $outdir/before.2
echo content3 > $outdir/before.3
../tools/snapmgr create $path --label="$( date -d @$oneweek2hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
echo content4 > $outdir/during.4
../tools/snapmgr create $path --label="$( date -d @$oneweek1hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
echo content5 > $outdir/during.4
echo content6 > $outdir/during.5
echo content7 > $outdir/during.6
rm -f $outdir/before.2
../tools/snapmgr create $path --label="$( date -d @$oneweek0hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
rm -f $outdir/during.5
echo content8 > $outdir/before.1
../tools/snapmgr create $path --label="$( date -d @$now3hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
rm -f $outdir/during.6
../tools/snapmgr create $path --label="$( date -d @$now2hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
echo content3 > $outdir/current.3
../tools/snapmgr create $path --label="$( date -d @$now1hr '+%Y-%m-%dT%H:%M:%S%z')" --noprompt
rm -f $outdir/during.6
rm -f $outdir/during.4
echo content1 > $outdir/after.1
echo content2 > $outdir/after.2

echo "# Success"
