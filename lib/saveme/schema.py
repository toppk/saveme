
#
# schema - explains the scripts directory
#

ROUTINES = {
    'list-snap': { 'script': 'ssfs-list-snap.sh',
                   'generates-commands': False },
    'delete-snap': { 'script': 'ssfs-delete-snap.sh',
                     'generates-commands': True },
    'take-snap': { 'script': 'ssfs-take-snap.sh',
                   'generates-commands': True },
    'generate-checksum': { 'script': 'file-generate-chksum.sh',
                           'generates-commands': False },
    'add-partition-table': { 'script': 'disk-add-part.sh',
                             'generates-commands': True },
    'verify-partition-table': { 'script': 'disk-verify-part.sh',
                                'generates-commands': False },
    'generate-luks-key': { 'script': 'core-gen-key.sh',
                           'generates-commands': True },
    
}

SEQUENCES = {
    'disk-to-arfs' : ['add-partition-table', 'verify-partition-table', 'generate-luks-key']
}

def findscript(routine):
    return ROUTINES[routine]

def getsequence(sequence):
    return SEQUENCES[sequence]
