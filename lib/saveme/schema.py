
#
# schema - explains the scripts directory
#

ROUTINES = {
    'list-snap': 'ssfs-list-snap.sh',
    'delete-snap': 'ssfs-delete-snap.sh',
    'take-snap': 'ssfs-take-snap.sh',
    'generate-checksum': 'file-generate-chksum.sh',
    'add-partition-table': 'disk-add-part.sh'
    'generate-luks-key': 'core-gen-key.sh'
}

SEQUENCES = {
    'disk-to-arfs' : ['add-partition-table', 'generate-luks-key']
}

def findscript(routine):
    return ROUTINES[routine]
