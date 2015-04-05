
#
# schema - explains the scripts directory
#

ROUTINES = {
    'list-snap': 'ssfs-list-snap.sh',
    'delete-snap': 'ssfs-delete-snap.sh',
    'take-snap': 'ssfs-take-snap.sh'
}

def findscript(routine):
    return ROUTINES[routine]
