
#
#
#

from dateutil import parser
import subprocess
import time
#


def runcommand(args):
    sp = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = sp.communicate()
    retcode = sp.wait()
    return retcode,out.decode("utf-8"),err.decode("utf-8")
        
def getcurtime():
    return int(time.strftime("%s", time.gmtime()))

    
def parsedate(datestr):
    date = parser.parse(datestr.replace("_"," "))
    return int(date.strftime("%s"))

#[root@static lowlevel.1427596324]# date '+%Y%m%d_%H:%M:%S_%z'
#20150329_23:35:41_-0400
