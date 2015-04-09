
#
# schema - explains the scripts directory
#

ROUTINES = {
    'list-snap': {'script': 'ssfs-list-snap.sh',
                  'args': ['path'],
                  'generates-commands': False},
    'delete-snap': {'script': 'ssfs-delete-snap.sh',
                    'args': ['path', 'label'],
                    'generates-commands': True},
    'take-snap': {'script': 'ssfs-take-snap.sh',
                  'args': ['path'],
                  'generates-commands': True},
    'get-filesystem-capacity': {'script': 'sys-fs-capacity.sh',
                          'args': ['path'],
                          'generates-commands': False},
    'generate-checksum': {'script': 'file-generate-chksum.sh',
                          'args': ['path'],
                          'generates-commands': False},
    'verify-luks-partition': {'script': 'part-verify-luks.sh',
                              'args': ['part'],
                              'generates-commands': False},
    'verify-archive-filesystem': {'script': 'part-verify-arfs.sh',
                                  'args': ['part', 'arid'],
                                  'generates-commands': False},
    'check-archive-filesystem': {'script': 'part-check-arfs.sh',
                                 'args': ['arid'],
                                 'generates-commands': False},
    'add-archive-filesystem': {'script': 'part-add-arfs.sh',
                               'args': ['part', 'arid'],
                               'generates-commands': True},
    'mount-archive-filesystem': {'script': 'sys-attach-arfs.sh',
                                 'args': ['arid'],
                                 'generates-commands': True},
    'add-luks-partition': {'script': 'part-add-luks.sh',
                           'args': ['part', 'keyf'],
                           'generates-commands': True},
    'add-partition-table': {'script': 'disk-add-part.sh',
                            'args': ['disk'],
                            'generates-commands': True},
    'verify-partition-table': {'script': 'disk-verify-part.sh',
                               'args': ['disk'],
                               'generates-commands': False},
    'verify-arid-unused': {'script': 'core-verify-arid.sh',
                           'args': ['arid'],
                           'generates-commands': False},
    'generate-luks-key': {'script': 'core-gen-key.sh',
                          'args': [],
                          'generates-commands': True}
}

def findscript(routine):
    return ROUTINES[routine]
