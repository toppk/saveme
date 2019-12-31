#
#
#

from .cfg import getsnapshotpattern as _cfg_snapshot_pattern
from .external import getcurtime, match, parsedate
from .utils import StopException, TaskRunner, parsepolicy


def deletesnapshot(path, label):
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.setvalue("label", label)
    return runner.runstep("delete-snap")


def create(path, label=None, promptuser=True):
    runner = TaskRunner()
    runner.setvalue("path", path)
    options = []
    if label is not None:
        options += [("label", label)]
    return runner.runstep("take-snap", options=options, promptuser=promptuser)


def listsnapshot(path):
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.runstep("list-snap")
    if runner.getretcode() == 0:
        if runner.getout() != "":
            print(runner.getout())
    return runner.getretcode()


def manage(path, policy=None, promptuser=None):
    res = []
    try:
        parsepolicy(policy)
    except ValueError as err:
        print("issues with policy [%s]" % (err))
        return 3

    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.runstep("list-snap")
    if runner.getretcode() != 0:
        return runner.getretcode()
    if runner.getout() == "":
        print("no snapshots to manage")
        return 0
    snapshots = runner.getout().split("\n")
    tsnap = []
    for snap in snapshots:
        if match(snap, _cfg_snapshot_pattern()):
            tsnap += [snap]
        else:
            print(" (skipping: %s - does not match expected pattern)" % snap)
    res = culltimeline(tsnap, policy, getcurtime())
    if res is not None or len(res) > 0:
        runner.setvalue("label", "-")
        stdin = "\n".join(res) + "\n"
        try:
            runner.runstep("delete-snap", stdin=stdin, promptuser=promptuser)
        except StopException:
            print("user selected no")
            return 2

        # if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
    return runner.getretcode()


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
        # print("need to check %s vs %s is delt=%s" % (snapdate,now,delta))
        for rangespec in prunemap:
            # print(" eval  ra= %s, %s, %s, %s " % (rangespec) )
            if delta >= rangespec[0] and (
                (rangespec[1] is None) or (delta <= rangespec[1])
            ):
                keep = False
                # print("old=%s %s"%(old,rangespec[2]))
                if rangespec[2] == "none":
                    pass
                elif rangespec[2] == "all":
                    keep = True
                elif old is None:
                    keep = True
                elif snapdate[0] - old > rangespec[2]:
                    keep = True
                old = snapdate[0]

                if keep is False:
                    # print("kill %s cuz %s [%s]" % (snapdate,keep,rangespec[3]))
                    res += [snapdate[1]]
    res.sort(reverse=True)
    return res
