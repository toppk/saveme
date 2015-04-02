#!/bin/bash

function runme()
{

    sleep=0
    if [ "$1" == "--sleep" ]; then
	sleep=10
	shift
    fi
    id=$1
    shift
    comm=$*
    echo "# STARTING: id=$id comm=[$comm]"
    $comm > $logdir/$id.out 2> $logdir/$id.err
    err=$?
    if [ $err -ne 0 ]; then
	echo "#  FAILURE: error $err during starting $id"
	return 1
    fi
    echo "#  SUCCESS: started $id"
    echo "#  RUNNING: id=$id comm=[bash -e ./$id.out] contents=[$( tr '\n' ';' < $logdir/$id.out )]"
    if [ $sleep -ne 0 ]; then
	echo "#   notice: sleeping for $sleep seconds"
	sleep $sleep
    fi
    bash -e $logdir/$id.out > $logdir/${id}_RUN.out 2> $logdir/${id}_RUN.err
    err=$?
    if [ $err -ne 0 ]; then
	echo "#  FAILURE: error $err during running $id"
	return 2
    fi
    . <( cat $logdir/$id.out  | sed -n  "/^#/s/.*'\(.*\)':'\(.*\)'$/\1=\2/p" )
}


testname=${testname:-generic}

if [ -z "$logdir" ] ; then
    logdir="./output/$testname.$( date +%s )"
    echo "#   notice: logs are $logdir"
    mkdir -p $logdir
fi



if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    runme "should-fail-starting" ls -d /asdf / && exit || echo "#  SUCCESS: it failed above us"
    runme "should-fail-running" echo ls -d /asdf / && exit || echo "#  SUCCESS: it failed above us"
    runme "should-succeed" echo ls -d / && echo "#  SUCCESS: it returned" || exit
    key=""
    runme "should-passfact" echo "# 'key':'value'" || exit
    [ "$key" != "value" ] && echo "#  FAILURE: error seeing key during test" || echo "#  SUCCESS: seeing value==$key during test"
    key2=""
    runme --sleep "should-passfact-double" echo -e "# 'key':'value'\n# 'key2':'value2'" || exit
    [ "$key2" != "value2" ] && echo "#  FAILURE: error seeing key2 during test" || echo "#  SUCCESS: seeing key2 during test"
fi
