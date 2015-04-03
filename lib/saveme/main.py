
#
#
#

from .utils import parsepolicy,launch
from .external import parsedate,runcommand,getcurtime,match
from .cfg import getscriptsdir as _cfg_scripts_directory
from .cfg import getsnapshotpattern as _cfg_snapshot_pattern
from .schema import findscript

def deletesnapshot(path,label):
    args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("delete-snap")),path,label]

    retcode, out, err = runcommand(args)
    if retcode == 0:
        if launch(out):
            return 0
        else:
            return 3
    else:
        print("delsnap gen issues [%s][%s][%d]"%(out,err,retcode))
        return 1
   
def create(path,label=None):
    
    args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("take-snap")),path]
    
    if label is not None:
        args += [ "--label=%s" % label ]

    retcode, out, err = runcommand(args)
    if retcode == 0:
        if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
            print("No action needed")
            return 0
    else:
        print("issues with execution [%s][%s][%d]"%(out,err,retcode))
        return 1

    if launch(out):
        return 0
    else:
        return 2
  
def listsnapshot(path):
    args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("list-snap")),path]

    #
    retcode, out, err = runcommand(args)
    if retcode != 0:
        print("issues with listsnap [%s][%s][%d]"%(out,err,retcode))
        return 10
    snap = out.strip().split('\n')
    tsnap = []
    for s in snap:
        if match(s,_cfg_snapshot_pattern()):
            print("%s" % s)
        else:
            print("%s #ignored" % s)


def manage(path,policy=None):
    res = []
    prunemap = parsepolicy(policy)
    args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("list-snap")),path]

    #
    retcode, out, err = runcommand(args)
    if retcode != 0:
        print("issues with listsnap [%s][%s][%d]"%(out,err,retcode))
        return 10
    snap = out.strip().split('\n')
    tsnap = []
    for s in snap:
        if match(s,_cfg_snapshot_pattern()):
            tsnap += [s]
        else:
            print(" (skipping snapshot: %s - does not match expected pattern)" % s)
    res = culltimeline(tsnap,policy,getcurtime())
    if res is not None or len(res) > 0:
        args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("delete-snap")),path,"-"]

        #
        retcode, out, err = runcommand(args,stdin="\n".join(res)+"\n")
        if retcode == 0:
          if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
              print("No action needed")
              return 0
          if launch(out):
                return 0
          else:
                return 3
        else:
            print("yoyo[%s][%s][%d]"%(out,err,retcode))
    return 0

    
def culltimeline(datearr,policy,now):
    res = []
    prunemap = parsepolicy(policy)
    old = None
    dates = []
    for sdatestr in datearr:
        dates += [ (parsedate(sdatestr),sdatestr) ]
    dates.sort()
    for snapdate in dates:
        delta = now - snapdate[0]
        # print("need to check %s vs %s is delt=%s" % (snapdate,now,delta))
        for ra in prunemap:
            if delta >= ra[0] and ( (delta <= ra[1]) or ( ra[1] is None) ):
                keep = False
                #print("old=%s %s"%(old,ra[2]))
                if ra[2] == "none":
                    pass
                elif ra[2] == "all":
                    keep = True
                elif old is None:
                    keep = True
                elif snapdate[0]-old > ra[2]:
                    keep = True
                
                old = snapdate[0]

                if keep is False:
                    # print("going to kill %s cuz %s [%s]" % (snapdate,keep,ra[3]))
                    res += [snapdate[1]]
    res.sort(reverse=True)
    return res


            
