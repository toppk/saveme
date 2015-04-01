
#
#
#

from .main import manage
from .cfg import getdefsnappol as _cfg_default_snapshot_policy

class CommandLine:
    
    i = 123

    def usage(self,proc):
        print("usage: %s\n\nCOMMANDS\n manage <path> [--policy=XXX]\n   snap <path>\n\nOPTIONS\n policy = [0-9]*[hr,dy,wk,yr]" % proc)

    def go(self,args):
        if len(args) == 1:
            self.usage(args[0])
        elif args[1] == "manage":
            if len(args) == 2:
                print("manage: you must specify <path>")
                return 1
            elif args[2] in ( "--help", "help" ):
                print("usage: manage  <path> [--policy=XXX]\nexample policy=\"1wk+\"")
                return 12

            pool = args[2]
            policy = _cfg_default_snapshot_policy()
            for options in args[3:]:
                if options.startswith("--policy="):
                    policy=options[9:]
                else:
                    print ("unknown option = %s" % options)
            print( "managing %s with pol[%s] " % (pool,policy))
            manage(pool,policy)
        elif args[1] == "snap":
            pool = args[2]
            for options in args[3:]:
                print ("option = %s" % options)
            print( "create snap for %s " % pool)
        return 12

    def help(self):
        print('i am suppossed to go, check usage')
        return True

