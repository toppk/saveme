
#
#
#

settings = {
    'default-policy' : '0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none',
    }

def getdefaultpolicy():
    return settings['default-policy']
