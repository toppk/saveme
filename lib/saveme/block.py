
#
#
#

from .utils import TaskRunner
from .external import getid

def genarid():
    return getid()

def makearfsfromdisk(disk):
    runner = TaskRunner()
    runner.setvalue('disk',disk)
    for step in ('add-partition-table',
                 'verify-partition-table',
                 'generate-luks-key',
                 'add-luks-partition'):
        runner.runstep(step)
    # cprt will be the part for the rest of the steps
    runner.addalias('cprt','part')
    runner.runstep('verify-luks-partition')
    runner.setvalue('arid',genarid())
    runner.runstep('verify-arid-unused')
    for step in ('add-archive-filesystem',
                 'verify-archive-filesystem',
                 'mount-archive-filesystem',
                 'check-archive-filesystem'):
        runner.runstep(step)
 
