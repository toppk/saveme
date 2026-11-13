from typing import List, Tuple

from .cfg import getsnapshotpattern as _cfg_snapshot_pattern
from .external import getcurtime, match, parsedate
from .utils import StopException, TaskRunner, parsepolicy


def deletesnapshot(path: str, label: str) -> int:
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.setvalue("label", label)
    try:
        return runner.runstep("delete-snap")
    except StopException:
        return runner.getretcode()


def create(path: str, label: str | None = None, promptuser: bool = True) -> int:
    runner = TaskRunner()
    runner.setvalue("path", path)
    options: List[Tuple[str, str]] = []
    if label is not None:
        options += [("label", label)]
    try:
        return runner.runstep("take-snap", options=options, promptuser=promptuser)
    except StopException:
        return runner.getretcode()


def listsnapshot(path: str) -> int:
    runner = TaskRunner()
    runner.setvalue("path", path)
    try:
        runner.runstep("list-snap")
    except StopException:
        return runner.getretcode()
    if runner.getretcode() == 0:
        if runner.getout() != "":
            print(runner.getout())
    return runner.getretcode()


def manage(path: str, policy: str | None = None, promptuser: bool = True) -> int:
    res = []
    try:
        assert policy is not None
        parsepolicy(policy)
    except ValueError as err:
        print("issues with policy [%s]" % (err))
        return 3

    runner = TaskRunner()
    runner.setvalue("path", path)
    try:
        runner.runstep("list-snap")
    except StopException:
        return runner.getretcode()
    if runner.getretcode() != 0:
        return runner.getretcode()
    if runner.getout() == "":
        print("no snapshots to manage")
        return 0
    snapshots = runner.getout().split("\n")
    tsnap: List[str] = []
    for snap in snapshots:
        if match(snap, _cfg_snapshot_pattern()):
            tsnap += [snap]
        else:
            print(" (skipping: %s - does not match expected pattern)" % snap)
    res = culltimeline(tsnap, policy, getcurtime())
    if res:
        runner.setvalue("label", "-")
        stdin = "\n".join(res) + "\n"
        try:
            runner.runstep("delete-snap", stdin=stdin, promptuser=promptuser)
        except StopException:
            return runner.getretcode()

        # if len([i for i in out.split("\n") if i != "" and i[0] != "#"]) == 0:
    return runner.getretcode()


def culltimeline(datearr: List[str], policy: str, now: int) -> List[str]:
    res: List[str] = []
    prunemap = parsepolicy(policy)
    old = None
    dates: List[Tuple[int, str]] = []
    for sdatestr in datearr:
        dates += [(parsedate(sdatestr), sdatestr)]
    dates.sort()
    for snapdate in dates:
        delta = now - snapdate[0]
        # print("need to check %s vs %s is delt=%s" % (snapdate,now,delta))
        for rangespec in prunemap:
            # print(" eval  ra= %s, %s, %s, %s " % (rangespec) )
            if delta >= rangespec[0] and (
                (rangespec[1] is None) or (delta < rangespec[1])
            ):
                keep = False
                # print("old=%s %s"%(old,rangespec[2]))
                if rangespec[2] == "none":
                    pass
                elif rangespec[2] == "all":
                    keep = True
                elif old is None:
                    keep = True
                elif (
                    isinstance(rangespec[2], int) and snapdate[0] - old >= rangespec[2]
                ):
                    keep = True
                if keep:
                    old = snapdate[0]

                if keep is False:
                    # print("kill %s cuz %s [%s]" % (snapdate,keep,rangespec[3]))
                    res += [snapdate[1]]
    res.sort(reverse=True)
    return res
