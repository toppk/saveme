import sys
from typing import Callable, List, TextIO

from .block import genarid, makearfsfromdisk
from .cfg import getdefsnappol as _cfg_default_snapshot_policy
from .mirror import (
    addbackup,
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
from .types import NoDatabase

# sysexits EX_USAGE, clear of 1 (commands failed) and 2 (declined)
USAGE = 64
HELP = ("help", "-h", "--help")


def _err(msg: str) -> int:
    print(msg, file=sys.stderr)
    return USAGE


class CommandLine:
    def __init__(self) -> None:
        pass

    def mirroradm(self, args: List[str]) -> int:
        def usage(proc: str, out: TextIO = sys.stdout) -> None:
            print(
                """usage: %s

 COMMANDS
           index <path>
    list-indexes
register-archive <path>
   list-archives
          backup <volumeid>
  missing-backup
  provide-backup <checksum> <archiveid> <blobchksum> <blobkey> <blobsize>
        checksum <volumeid>
  missing-chksum
  provide-chksum  <volumeid> <fileid> <checksum>
         resetdb""" % proc,
                file=out,
            )

        if len(args) == 1:
            usage(args[0], sys.stderr)
            return USAGE
        if args[1] in HELP:
            usage(args[0])
            return 0
        try:
            return self._mirroradm(args, usage)
        except NoDatabase as err:
            print(
                "mirroradm: database directory %s does not exist" % err, file=sys.stderr
            )
            return 1

    def _mirroradm(self, args: List[str], usage: Callable[[str, TextIO], None]) -> int:
        status = 0
        if args[1] == "provide-chksum":
            if len(args) != 5:
                status = _err(
                    "provide-chksum: you must specify <volumeid> <fileid> <checksum>"
                )
            else:
                addsum(int(args[2]), args[3], args[4])
        elif args[1] == "missing-chksum":
            missingsum()
        elif args[1] == "checksum":
            if len(args) != 3:
                status = _err("checksum: you must specify <volumeid>")
            else:
                try:
                    volumeid = int(args[2])
                except ValueError:
                    return _err("volumeid must be an integer")
                status = checksumvolume(volumeid)
        elif args[1] == "provide-backup":
            if len(args) != 7:
                status = _err(
                    "provide-backup: you must specify <checksum> <archiveid>"
                    " <blobchksum> <blobkey> <blobsize>"
                )
            else:
                try:
                    archiveid, blobsize = int(args[3]), int(args[6])
                except ValueError:
                    return _err("archiveid and blobsize must be integers")
                addbackup(args[2], archiveid, args[4], args[5], blobsize)
        elif args[1] == "missing-backup":
            missingbackup()
        elif args[1] == "backup":
            if len(args) != 3:
                status = _err("backup: you must specify <volumeid>")
            else:
                try:
                    volumeid = int(args[2])
                except ValueError:
                    return _err("volumeid must be an integer")
                status = backupvolume(volumeid)
        elif args[1] == "list-archives":
            listarchives()
        elif args[1] == "list-indexes":
            listvolumes()
        elif args[1] == "resetdb":
            createdb()
        elif args[1] == "register-archive":
            if len(args) != 3:
                status = _err("register-archive: you must specify <path>")
            else:
                path = args[2]
                registerarchive(path)
        elif args[1] == "index":
            if len(args) != 3:
                status = _err("index: you must specify <path>")
            else:
                path = args[2]
                status = index(path)
        else:
            usage(args[0], sys.stderr)
            status = _err("not a valid action: %s" % args[1])
        return status

    def disktool(self, args: List[str]) -> int:
        def usage(proc: str, out: TextIO = sys.stdout) -> None:
            print(
                """usage: %s

COMMANDS
 disk-to-arfs <disk>
 generate-arid

OPTIONS
 disk = disk to use (e.g. hda)""" % proc,
                file=out,
            )

        if len(args) == 1:
            usage(args[0], sys.stderr)
            status = USAGE
        elif args[1] in HELP:
            usage(args[0])
            status = 0
        elif args[1] == "generate-arid":
            if len(args) != 2:
                status = _err("generate-arid takes no arguments")
            else:
                print("%s" % genarid())
                status = 0
        elif args[1] == "disk-to-arfs":
            if len(args) != 3:
                status = _err("disk-to-arfs: you must specify <disk>")
            else:
                disk = args[2]
                status = makearfsfromdisk(disk)
        else:
            usage(args[0], sys.stderr)
            status = _err("not a valid action: %s" % args[1])
        return status

    def snapmgr(self, args: List[str]) -> int:
        def usage(proc: str, out: TextIO = sys.stdout) -> None:
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
 noprompt = will take action, no pause for confirmation""" % proc,
                file=out,
            )

        if len(args) == 1:
            usage(args[0], sys.stderr)
            status = USAGE
        elif args[1] in HELP:
            usage(args[0])
            status = 0
        elif args[1] == "manage":
            if len(args) == 2:
                status = _err("manage: you must specify <path>")
            elif args[2] in HELP:
                print(
                    'usage: manage <path> [--policy=XXX] [--noprompt]\n example --policy="1wk+: none"'
                )
                status = 0
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
                        return _err("unknown option = %s" % options)
                print(
                    'Managing snapshots for path="%s" with policy="%s" '
                    % (pool, policy)
                )
                status = manage(pool, policy, promptuser=promptuser)
        elif args[1] == "list":
            if len(args) == 2:
                status = _err("list: you must specify <path>")
            else:
                pool = args[2]
                label = None
                for options in args[3:]:
                    return _err("unknown option = %s" % options)
                status = listsnapshot(pool)
        elif args[1] == "create":
            if len(args) == 2:
                status = _err("create: you must specify <path>")
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
                        return _err("unknown option = %s" % options)
                status = create(pool, label=label, promptuser=promptuser)
        elif args[1] == "delete":
            if len(args) < 4:
                status = _err("delete: you must specify <path> <label>")
            else:
                pool = args[2]
                label = args[3]
                for options in args[4:]:
                    return _err("unknown option = %s" % options)
                status = deletesnapshot(pool, label)
        else:
            usage(args[0], sys.stderr)
            status = _err("not a valid action: %s" % args[1])
        return status
