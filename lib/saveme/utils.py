
#
#
#
from .external import runcommand

def launch(cmds, promptuser=True):
    if promptuser:
        print("\nPLEASE CONFIRM THE FOLLOWING ACTION\n---\n%s\n---"%"\n".join([i for i in cmds.split("\n") if i != "" and i[0] != "#"]))
        response = input("Do you wish to launch? y/n ")
    else:
        print("\nAUTORUNNING THE FOLLOWING ACTION\n---\n%s\n---"%"\n".join([i for i in cmds.split("\n") if i != "" and i[0] != "#"]))

    if not promptuser or response == "y":
        args = ["/bin/bash", "-e", "-c", cmds]
        retcode, out, err = runcommand(args)
        if retcode == 0:
            print("Success, got output\n---\n%s---"% out)
        else:
            print("Error: out,err,exit [%s][%s][%d]"%(out, err, retcode))
            return False
    return True


def parsepolicy(policystr):
    rules = []
    for rule in policystr.split(","):
        rule = rule.strip()
        (ra, sc) = rule.split(":")
        sc = sc.strip()
        ra = ra.strip()
        start = None
        end = None
        if sc not in ("all", "none"):
            sc = parsehdate(sc)
        if ra.find("-") > 0:
            (start, end) = ra.split("-")
            (start, end) = (parsehdate(start), parsehdate(end))
        elif ra.endswith("+"):
            start = parsehdate(ra[:-1])
        else:
            print("this is bad")
        if end is not None and start > end:
            raise ValueError('cannot end before you start [%s]'% ra)
        rules += [(start, end, sc, rule)]

    # need to sort and quality check the rules (and fill any gaps)
    return rules

def parsehdate(timestr):
    # no mo(nth) as there isn't a time definition of a month.
    time = None
    timestr = timestr.strip()
    if timestr == "0":
        time = 0
    elif timestr.endswith("yr"):
        time = int(timestr[:-2]) * 365 * 24 * 60 * 60
    elif timestr.endswith("mo"):
        # I said no month
        print("no mo(nth) support")
    elif timestr.endswith("wk"):
        time = int(timestr[:-2]) * 7 * 24 * 60 * 60
    elif timestr.endswith("dy"):
        time = int(timestr[:-2]) * 24 * 60 * 60
    elif timestr.endswith("hr"):
        time = int(timestr[:-2]) * 60 * 60
    elif timestr.endswith("mi"):
        time = int(timestr[:-2]) * 60
    elif timestr.endswith("se"):
        time = int(timestr[:-2])
    return time
