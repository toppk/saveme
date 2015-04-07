
#
#
#

from .utils import parsepolicy, launch
from .external import parsedate, runcommand, getcurtime, match, getrandom, getid
from .cfg import getscriptsdir as _cfg_scripts_directory
from .cfg import getsnapshotpattern as _cfg_snapshot_pattern
from .schema import findscript

def genarid():
    return getid()

def makearfsfromdisk(disk):
    args = ["/bin/bash", "%s/%s"%(_cfg_scripts_directory(),
                                  findscript("delete-snap")), disk]

    print("ran[%s]"% getrandom(64))
    retcode, out, err = runcommand(args)
    if retcode == 0:
        if launch(out):
            return 0
        else:
            return 3
    else:
        print("delsnap gen issues [%s][%s][%d]"%(out, err, retcode))
        return 1
