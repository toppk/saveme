
#
#
#

import subprocess
import time
import os
import re
from datetime import datetime,timezone
#

def runcommand(args,stdin=None):
    if stdin is not None:
        sp = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ, PATH="/bin:/sbin"))
        out,err = sp.communicate(input=bytes(stdin,"utf-8"))
    else:
        sp = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ, PATH="/bin:/sbin"))
        out,err = sp.communicate()
    
    retcode = sp.wait()
    return retcode,out.decode("utf-8"),err.decode("utf-8")
        
def getcurtime():
    return int(time.strftime("%s", time.gmtime()))

    
def parsedate(ts):
    return int(datetime.strptime(ts[:-6],"%Y%m%d_%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()) - (int(ts[-2:])*60 + 60 * 60 * int(ts[-4:-2]) * int(ts[-5:-4]+'1'))

def match(string,pattern):
    return re.search("^%s$"%pattern,string) is not None

#[root@static lowlevel.1427596324]# date '+%Y%m%d_%H:%M:%S_%z'
#20150329_23:35:41_-0400
