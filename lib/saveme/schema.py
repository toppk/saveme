#
# schema - explains the scripts directory
#
from .types import Routine

ROUTINES = {
    "list-snap": Routine(
        script="ssfs-list-snap.sh", args=["path"], generates_commands=False
    ),
    "delete-snap": Routine(
        script="ssfs-delete-snap.sh", args=["path", "label"], generates_commands=True
    ),
    "take-snap": Routine(
        script="ssfs-take-snap.sh", args=["path"], generates_commands=True
    ),
    "get-filesystem-capacity": Routine(
        script="sys-fs-capacity.sh", args=["path"], generates_commands=False
    ),
    "generate-checksum": Routine(
        script="file-generate-chksum.sh", args=["path"], generates_commands=False
    ),
    "verify-luks-partition": Routine(
        script="part-verify-luks.sh", args=["part"], generates_commands=False
    ),
    "verify-archive-filesystem": Routine(
        script="part-verify-arfs.sh", args=["part", "arid"], generates_commands=False
    ),
    "check-archive-filesystem": Routine(
        script="part-check-arfs.sh", args=["arid"], generates_commands=False
    ),
    "add-archive-filesystem": Routine(
        script="part-add-arfs.sh", args=["part", "arid"], generates_commands=True
    ),
    "mount-archive-filesystem": Routine(
        script="sys-attach-arfs.sh", args=["arid"], generates_commands=True
    ),
    "add-luks-partition": Routine(
        script="part-add-luks.sh", args=["part", "keyf"], generates_commands=True
    ),
    "add-partition-table": Routine(
        script="disk-add-part.sh", args=["disk"], generates_commands=True
    ),
    "verify-partition-table": Routine(
        script="disk-verify-part.sh", args=["disk"], generates_commands=False
    ),
    "verify-arid-unused": Routine(
        script="core-verify-arid.sh", args=["arid"], generates_commands=False
    ),
    "generate-luks-key": Routine(
        script="core-gen-key.sh", args=[], generates_commands=True
    ),
}


def findscript(routine: str) -> Routine:
    return ROUTINES[routine]
