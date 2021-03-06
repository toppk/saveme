import os
import queue
import random
import re
import string
import subprocess
import time
from datetime import datetime, timezone
from stat import S_ISDIR
from typing import Generator, List, Tuple


def abspath(path: str) -> str:
    return os.path.abspath(path)


def getid() -> str:
    return getrandom(5, justalphanum=True)


def getrandom(length: int, justalphanum: bool = False) -> str:
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    alphas = string.ascii_lowercase + string.ascii_uppercase
    if not justalphanum:
        chars += "+-"
    # from collections import OrderedDict as od
    # d = od()
    # for letter in chars:
    #    d[letter] = 0
    #    for i in range(0,10000):
    #        for c in ''.join(chars[c % len(chars)] for c in os.urandom(64)):
    #            d[c] += 1
    # print d
    return random.SystemRandom().choice(alphas) + "".join(
        [random.SystemRandom().choice(chars) for i in range(length - 1)]
    )


def indexer(path: str) -> Generator[Tuple[str, os.stat_result], None, None]:
    if not os.path.isdir(path):
        raise ValueError("path %s is not a directory" % path)
    # print("supposed to index %s to %s" % (path,_cfg_database_directory()))
    if path[-1] != "/":
        path += "/"
    yield (".", os.lstat(path))
    myqueue: queue.Queue = queue.Queue()
    myqueue.put(path)
    while not myqueue.empty():
        entry = myqueue.get()
        for filename in os.listdir(entry):
            filepath = "%s%s" % (entry, filename)
            res = os.lstat(filepath)
            if S_ISDIR(res.st_mode):
                myqueue.put(filepath + "/")
            yield (filepath[len(path) :], res)


def runcommand(args: List[str], stdin: str = None) -> Tuple[int, str, str]:
    if stdin is not None:
        proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PATH="/bin:/sbin:/usr/bin:/usr/sbin"),
        )
        out, err = proc.communicate(input=bytes(stdin, "utf-8"))
    else:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PATH="/bin:/sbin:/usr/bin:/usr/sbin"),
        )
        out, err = proc.communicate()
    retcode = proc.wait()
    return retcode, out.decode("utf-8"), err.decode("utf-8")


def getcurtime() -> int:
    return int(time.time() * 1e6)


def epoch2iso(epochmicros: int) -> str:
    thedate = datetime.fromtimestamp(epochmicros / 1e6)
    thedate = datetime.fromtimestamp(time.time())
    strdate = thedate.strftime("%Y-%m-%dT%H:%M:%S")
    minute = (time.localtime().tm_gmtoff / 60) % 60
    hour = ((time.localtime().tm_gmtoff / 60) - minute) / 60
    utcoffset = "%.2d%.2d" % (hour, minute)
    if utcoffset[0] != "-":
        utcoffset = "+" + utcoffset
    return strdate + utcoffset


def parsedate(timespec: str) -> int:
    pattern = "%Y-%m-%dT%H:%M:%S"
    datestr = timespec[:-5]
    sign = int(timespec[-5:-4] + "1")
    hour = int(timespec[-4:-2])
    minute = int(timespec[-2:])
    utcdate = datetime.strptime(datestr, pattern).replace(tzinfo=timezone.utc)
    utcoffset = sign * (hour + minute)
    return int(1e6 * (int(utcdate.timestamp()) - utcoffset))


def match(string: str, pattern: str) -> bool:
    return re.search("^%s$" % pattern, string) is not None


# date +"%Y-%m-%dT%H:%M:%S%z" or date --iso-8601=seconds
# 2015-04-07T02:45:00+0000
