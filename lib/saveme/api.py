
#
#
#

from .main import manage,create,listsnapshot,deletesnapshot
from .cfg import getdefsnappol as _cfg_default_snapshot_policy

class CommandLine:
    
    i = 123

    def usage(self,proc):
        print("usage: %s\n\nCOMMANDS\n manage <path> [--policy=XXX]\n delete <path> <label>\n create <path> [--label=XXX]\n   list <path>\n\nOPTIONS\n policy = [0-9]*[hr,dy,wk,yr]\n label = use a manual id" % proc)

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
                    return 3
            print( "Managing snapshots for path=\"%s\" with policy=\"%s\" " % (pool,policy))
            return manage(pool,policy)
        elif args[1] == "list":
            if len(args) == 2:
                print("list: you must specify <path>")
                return 1
            pool = args[2]
            label = None
            for options in args[3:]:
                print ("unknown option = %s" % options)
                return 3
            listsnapshot(pool)
        elif args[1] == "create":
            if len(args) == 2:
                print("create: you must specify <path>")
                return 1
            pool = args[2]
            label = None
            for options in args[3:]:
                if options.startswith("--label="):
                    label=options[8:]
                else:
                    print ("unknown option = %s" % options)
                    return 3
            create(pool,label=label)
        elif args[1] == "delete":
            if len(args) < 4:
                print("delete: you must specify <path> <label>")
                return 1
            pool = args[2]
            label = args[3]
            for options in args[4:]:
                print ("unknown option = %s" % options)
                return 3
            deletesnapshot(pool,label)
        else:
            print("not a valid action")
            return 2
        return 12

    def help(self):
        print('i am suppossed to go, check usage')
        return True

