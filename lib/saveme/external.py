
#
#
#

import subprocess
import time
import os
import re
from datetime import datetime, timezone
#

def runcommand(args, stdin=None):
    if stdin is not None:
        proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=dict(os.environ, PATH="/bin:/sbin"))
        out, err = proc.communicate(input=bytes(stdin, "utf-8"))
    else:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=dict(os.environ, PATH="/bin:/sbin"))
        out, err = proc.communicate()
    retcode = proc.wait()
    return retcode, out.decode("utf-8"), err.decode("utf-8")

def getcurtime():
    return int(time.time() * 1e6)

def parsedate(timespec):
    pattern = "%Y%m%d_%H:%M:%S"
    datestr = timespec[:-6]
    sign = int(timespec[-5:-4]+'1')
    hour = int(timespec[-4:-2])
    minute = int(timespec[-2:])
    utcdate = datetime.strptime( datestr, pattern).replace(tzinfo=timezone.utc)
    utcoffset = sign * ( hour + minute )
    return 1e6 * (int(utcdate.timestamp()) - utcoffset)

def match(string, pattern):
    return re.search("^%s$"%pattern, string) is not None

#[root@static lowlevel.1427596324]# date '+%Y%m%d_%H:%M:%S_%z'
#20150329_23:35:41_-0400
