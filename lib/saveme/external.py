from dateutil import parser

def parsedate(datestr):
    date = parser.parse(datestr.replace("_"," "))
    return int(date.strftime("%s"))

#[root@static lowlevel.1427596324]# date '+%Y%m%d_%H:%M:%S_%z'
#20150329_23:35:41_-0400
