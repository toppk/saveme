
#
#
#
from dateutil import parser

def culltimeline(datearr,policy,now):
    res = []
    print("i'm not really thinking")
    return None # res
    
def parsedate(datestr):
    print("here is dates[%s]"%datestr)
    date = parser.parse(datestr.replace("_"," "))
    print("here is dated[%s]"%date)
    return int(date.strftime("%s"))

