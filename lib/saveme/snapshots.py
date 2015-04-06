
#
#
#

from .utils import parsepolicy, launch
from .external import parsedate, runcommand, getcurtime, match
from .cfg import getscriptsdir as _cfg_scripts_directory
from .cfg import getsnapshotpattern as _cfg_snapshot_pattern
from .schema import findscript

def deletesnapshot(path, label):
    args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                  findscript("delete-snap")), path, label]

    retcode, out, err = runcommand(args)
    if retcode == 0:
        if launch(out):
            return 0
        else:
            return 3
    else:
        print("delsnap gen issues [%s][%s][%d]"%(out, err, retcode))
        return 1

def create(path, label=None, promptuser=None):
    args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                  findscript("take-snap")), path]

    if label is not None:
        args += ["--label=%s" % label]

    retcode, out, err = runcommand(args)
    if retcode == 0:
        if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
            print("No action needed")
            return 0
    else:
        print("issues with execution [%s][%s][%d]"%(out, err, retcode))
        return 1

    if launch(out, promptuser=promptuser):
        return 0
    else:
        return 2

def listsnapshot(path):
    args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                  findscript("list-snap")), path]

    #
    retcode, out, err = runcommand(args)
    if retcode != 0:
        print("issues with listsnap [%s][%s][%d]"%(out, err, retcode))
        return 10
    snapshots = out.strip().split('\n')
    for snap in snapshots:
        if match(snap, _cfg_snapshot_pattern()):
            print("%s" % snap)
        elif snap != "":
            print("%s #ignored" % snap)


def manage(path, policy=None, promptuser=None):
    res = []
    try:
        parsepolicy(policy)
    except ValueError as err:
        print("issues with policy [%s]"%(err))
        return 3
    args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                  findscript("list-snap")), path]

    #
    retcode, out, err = runcommand(args)
    if retcode != 0:
        print("issues with listsnap [%s][%s][%d]"%(out, err, retcode))
        return 10
    snapshots = out.strip().split('\n')
    tsnap = []
    for snap in snapshots:
        if match(snap, _cfg_snapshot_pattern()):
            tsnap += [snap]
        else:
            print(" (skipping: %s - does not match expected pattern)" % snap)
    res = culltimeline(tsnap, policy, getcurtime())
    if res is not None or len(res) > 0:
        args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                      findscript("delete-snap")), path, "-"]

        #
        retcode, out, err = runcommand(args, stdin="\n".join(res)+"\n")
        if retcode == 0:
            if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
                print("No action needed")
                return 0
            if launch(out, promptuser=promptuser):
                return 0
            else:
                return 3
        else:
            print("error running cmd [%s][%s][%d]"%(out, err, retcode))
    return 0

def culltimeline(datearr, policy, now):
    res = []
    prunemap = parsepolicy(policy)
    old = None
    dates = []
    for sdatestr in datearr:
        dates += [(parsedate(sdatestr), sdatestr)]
    dates.sort()
    for snapdate in dates:
        delta = now - snapdate[0]
        #print("need to check %s vs %s is delt=%s" % (snapdate,now,delta))
        for rangespec in prunemap:
            #print(" eval  ra= %s, %s, %s, %s " % (rangespec) )
            if delta >= rangespec[0] and ((rangespec[1] is None) or (delta <= rangespec[1])):
                keep = False
                #print("old=%s %s"%(old,rangespec[2]))
                if rangespec[2] == "none":
                    pass
                elif rangespec[2] == "all":
                    keep = True
                elif old is None:
                    keep = True
                elif snapdate[0]-old > rangespec[2]:
                    keep = True
                old = snapdate[0]

                if keep is False:
                    # print("kill %s cuz %s [%s]" % (snapdate,keep,rangespec[3]))
                    res += [snapdate[1]]
    res.sort(reverse=True)
    return res
