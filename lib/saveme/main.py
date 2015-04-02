
#
#
#

from .utils import parsepolicy
from .external import parsedate,runcommand,getcurtime,match
from .cfg import getscriptsdir as _cfg_scripts_directory
from .schema import findscript

def manage(path,policy=None):
    res = []
    prunemap = parsepolicy(policy)
    args = ["/bin/bash","%s/%s"%(_cfg_scripts_directory(),findscript("list-snap")),path]
    retcode, out, err = runcommand(args)
    if retcode != 0:
        print("issues with pullsnap [%s][%s][%d]"%(out,err,retcode))
        return 10
    snap = out.strip().split('\n')
    tsnap = []
    for s in snap:
        if match(s,"^\d\d\d\d\d\d\d\d_\d\d:\d\d:\d\d_[-+]\d\d\d\d$"):
            tsnap += [s]
    print("yoyoyo %s" %tsnap)
    res = culltimeline(tsnap,policy,getcurtime())
    for keep in res:
        print(" will keep %s" % keep)
    return 0

    
def culltimeline(datearr,policy,now):
    res = []
    prunemap = parsepolicy(policy)
    print("i'm not really thinking [%s]"%(prunemap))
    old = None
    dates = []
    for sdatestr in datearr:
        dates += [ parsedate(sdatestr) ]
    dates.sort()
    for snapdate in dates:
        delta = now - snapdate
        print("need to check %s vs %s is delt=%s" % (snapdate,now,delta))
        for ra in prunemap:
            if delta >= ra[0] and ( (delta <= ra[1]) or ( ra[1] is None) ):
                try: 
                    print ("diff is %s" % (snapdate-old))
                except TypeError:
                    pass
                keep = False
                print ("ra is %s" % (ra[2]))
                if ra[2] == "none":
                    pass
                elif ra[2] == "all":
                    keep = True
                elif old is None:
                    keep = True
                    old = snapdate
                elif snapdate-old > ra[2]:
                    keep = True
                

                if keep is not False:
                    res += [snapdate]
                    print("going to keep %s cuz %s [%s]" % (snapdate,keep,ra[3]))
                else:
                    print("going to skip  %s [%s]" % (snapdate,ra[3]))
    res.sort(reverse=True)
    return res


            
