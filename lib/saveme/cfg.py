
#
# cfg - all configuration settings.  no intradepenencies, so depends on os,sys for bootstrapping
#

import os,sys

settings = {
    'default-snapshot-policy' : '0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none',
    'snapshot-pattern' : "^\d\d\d\d\d\d\d\d_\d\d:\d\d:\d\d_[-+]\d\d\d\d$",
    'scripts-directory' : None
}

def getsnapshotpattern():
    return settings['snapshot-pattern']

def getdefsnappol():
    return settings['default-snapshot-policy']

def getscriptsdir():
    return settings['scripts-directory']

# initialization/override methods
if settings['scripts-directory'] is None:
    settings['scripts-directory'] = os.path.abspath(os.path.dirname(sys.argv[0])  + "/../scripts")
