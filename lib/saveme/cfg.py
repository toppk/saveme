
#
# cfg - all configuration settings.  no intradepenencies,
#       so depends on os,sys for bootstrapping
#

import os, sys

SETTINGS = {
    'default-snapshot-policy' : '0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none',
    'snapshot-pattern' : r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d[-+]\d\d\d\d$",
    'scripts-directory' : None,
    'database-directory' : '/etc/saveme/db'
}

def getsnapshotpattern():
    return SETTINGS['snapshot-pattern']

def getdefsnappol():
    return SETTINGS['default-snapshot-policy']

def getdbdir():
    return SETTINGS['database-directory']

def getscriptsdir():
    return SETTINGS['scripts-directory']

# initialization/override methods
if SETTINGS['scripts-directory'] is None:
    SETTINGS['scripts-directory'] = os.path.abspath(
        os.path.dirname(sys.argv[0]) + "/../scripts"
    )
