#
#
#

from .block import genarid, makearfsfromdisk
from .cfg import getdefsnappol as _cfg_default_snapshot_policy
from .mirror import (
    addsum,
    backupvolume,
    checksumvolume,
    createdb,
    index,
    listarchives,
    listvolumes,
    missingbackup,
    missingsum,
    registerarchive,
)
from .snapshots import create, deletesnapshot, listsnapshot, manage


class CommandLine:
    def __init__(self):
        pass

    def mirroradm(self, args):
        status = 1

        def usage(proc):
            print(
                """usage: %s

 COMMANDS
           index <path>
    list-indexes
register-archive <path>
   list-archives
          backup <volumeid>
  missing-backup
  provide-backup <volumeid> <fileid> <checksum>
        checksum <volumeid>
  missing-chksum
  provide-chksum  <volumeid> <fileid> <checksum>
         resetdb"""
                % proc
            )

        if len(args) == 1:
            usage(args[0])
        elif args[1] == "provide-chksum":
            if len(args) != 5:
                print("provide: you must specify <volumeid> <fileid> <chksum>")
                status = 1
            else:
                addsum(int(args[2]), args[3], args[4])
        elif args[1] == "missing-chksum":
            missingsum()
        elif args[1] == "checksum":
            if len(args) != 3:
                print("checksum: you must specify <volumeid>")
                status = 2
            else:
                try:
                    volumeid = int(args[2])
                except ValueError:
                    print("volumeid must be an integer")
                    return 3
                status = checksumvolume(volumeid)
        elif args[1] == "provide-backup":
            if len(args) != 6:
                print("provide: you must specify <chksum> <blobsize> <blobchksum> -")
                status = 1
            else:
                addsum(int(args[2]), args[3], args[4])
        elif args[1] == "missing-backup":
            missingbackup()
        elif args[1] == "backup":
            if len(args) != 3:
                print("backup: you must specify <volumeid>")
                status = 2
            else:
                try:
                    volumeid = int(args[2])
                except ValueError:
                    print("volumeid must be an integer")
                    return 3
                status = backupvolume(volumeid)
        elif args[1] == "list-archives":
            listarchives()
        elif args[1] == "list-indexes":
            listvolumes()
        elif args[1] == "resetdb":
            createdb()
        elif args[1] == "register-archive":
            if len(args) != 3:
                print("register-archive: you must specify <path>")
                status = 4
            else:
                path = args[2]
                registerarchive(path)
        elif args[1] == "index":
            if len(args) != 3:
                print("index: you must specify <path>")
                status = 4
            else:
                path = args[2]
                index(path)
        else:
            print("not a valid action")
            status = 5
        return status

    def disktool(self, args):
        def usage(proc):
            print(
                """usage: %s

COMMANDS
 disk-to-arfs <disk>
 generate-arid

OPTIONS
 disk = disk to use (e.g. hda)"""
                % proc
            )

        status = 12
        if len(args) == 1:
            usage(args[0])
        elif args[1] == "generate-arid":
            if len(args) != 2:
                print("there are no arguments")
                status = 1
            else:
                print("%s" % genarid())
                status = 0
        elif args[1] == "disk-to-arfs":
            if len(args) != 3:
                print("disk-to-arfs: you must specify <disk>")
                status = 2
            else:
                disk = args[2]
                status = makearfsfromdisk(disk)
        else:
            print("not a valid action")
            status = 3
        return status

    def snapmgr(self, args):
        def usage(proc):
            print(
                """usage: %s

COMMANDS
 manage <path> [--policy=XXX] [--noprompt]
 delete <path> <label>
 create <path> [--label=XXX] [--noprompt]
   list <path>

OPTIONS
 policy = [0-9]*[hr,dy,wk,yr]
 label = use a manual id
 noprompt = will take action, no pause for confirmation"""
                % proc
            )

        status = 12
        if len(args) == 1:
            usage(args[0])
        elif args[1] == "manage":
            if len(args) == 2:
                print("manage: you must specify <path>")
                status = 1
            elif args[2] in ("--help", "help"):
                print(
                    """usage: manage  <path> [--policy=XXX] [--noprompt]
                example policy="1wk+\""""
                )
                status = 12
            else:
                pool = args[2]
                policy = _cfg_default_snapshot_policy()
                promptuser = True
                for options in args[3:]:
                    if options.startswith("--policy="):
                        policy = options[9:]
                    elif options == "--noprompt":
                        promptuser = False
                    else:
                        print("unknown option = %s" % options)
                        return 3
                print(
                    'Managing snapshots for path="%s" with policy="%s" '
                    % (pool, policy)
                )
                status = manage(pool, policy, promptuser=promptuser)
        elif args[1] == "list":
            if len(args) == 2:
                print("list: you must specify <path>")
                status = 1
            else:
                pool = args[2]
                label = None
                for options in args[3:]:
                    print("unknown option = %s" % options)
                    return 3
                status = listsnapshot(pool)
        elif args[1] == "create":
            if len(args) == 2:
                print("create: you must specify <path>")
                status = 1
            else:
                pool = args[2]
                label = None
                promptuser = True
                for options in args[3:]:
                    if options.startswith("--label="):
                        label = options[8:]
                    elif options == "--noprompt":
                        promptuser = False
                    else:
                        print("unknown option = %s" % options)
                        return 3
                status = create(pool, label=label, promptuser=promptuser)
        elif args[1] == "delete":
            if len(args) < 4:
                print("delete: you must specify <path> <label>")
                status = 1
            else:
                pool = args[2]
                label = args[3]
                for options in args[4:]:
                    print("unknown option = %s" % options)
                    return 3
                status = deletesnapshot(pool, label)
        else:
            print("not a valid action")
            status = 2
        return status

    def help(self):
        print("i am suppossed to go, check usage")
        return True
