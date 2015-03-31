
#
#
#
from dateutil import parser

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


def parsehdate(datestr):
    # no mo(nth) as there isn't a time definition of a month.
    datestr = datestr.strip()
    if datestr == "0":
        return 0
    if datestr.endswith("yr"):
        return int(datestr[:-2]) * 365 * 24 * 60 * 60
    if datestr.endswith("mo"):
        # I said no month
        print("no mo(nth) support")
    if datestr.endswith("wk"):
        return int(datestr[:-2]) * 7 * 24 * 60 * 60
    if datestr.endswith("dy"):
        return int(datestr[:-2]) * 24 * 60 * 60
    if datestr.endswith("hr"):
        return int(datestr[:-2]) * 60 * 60
    if datestr.endswith("mi"):
        return int(datestr[:-2]) * 60
    if datestr.endswith("se"):
        return int(datestr[:-2])
            
def parsepolicy(policystr):
    
    rules = []
    for rule in policystr.split(","):
        rule = rule.strip()
        (ra,sc) = rule.split(":")
        sc = sc.strip() 
        ra = ra.strip()
        start = None
        end = None
        if sc not in ("all","none"):
            sc = parsehdate(sc)
        if ra.find("-") > 0:
            (start,end) = ra.split("-")
            (start,end) = (parsehdate(start),parsehdate(end))
        elif ra.endswith("+"):
            start=parsehdate(ra[:-1])
        else:
            print("this is bad")
        rules += [(start,end,sc,rule)]

    # need to sort and quality check the rules (and fill any gaps)
    return rules

def parsedate(datestr):
    date = parser.parse(datestr.replace("_"," "))
    return int(date.strftime("%s"))

