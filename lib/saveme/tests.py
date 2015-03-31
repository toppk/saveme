import unittest
from main import CommandLine
cl=CommandLine()


import sys
print(" Running Python Version [%s] " % sys.version)


class TestMain(unittest.TestCase):

    _cl = None
    
    def setUp(self):
        from main import CommandLine
        self._cl = CommandLine()

    def test_cli_go(self):
        self.assertEqual( self._cl.go(), 12)

    def test_cli_help(self):
        self.assertEqual( self._cl.help(), True)

class TestUtil(unittest.TestCase):

    _parsedate = None
    from utils import culltimeline as _culltimeline
    
    def setUp(self):
        from utils import parsedate
        self._parsedate = parsedate

    def test_util_parsedate(self):
        # date '+%Y%m%d_%H:%M:%S_%z'
        self.assertEqual( self._parsedate('20150329_23:35:41_-0400'), 1427690141)


    def test_util_culltimeline(self):
        # date '+%Y%m%d_%H:%M:%S_%z'
        from utils import culltimeline as _culltimeline
        import pdb
        #pdb.set_trace()
        self.assertEqual(_culltimeline(['20150329_23:35:41_-0400'],
                                       "0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none",
                                       1427690151), [1427690141] )
        self.assertEqual(_culltimeline(['20150329_23:35:41_-0400','20150301_23:35:41_-0400','20150201_23:35:41_-0400'],
                                       "0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none",
                                       1427690151), [1427690141, 1425270941, 1422851741] )
        self.assertEqual(_culltimeline(['20150329_23:35:41_-0400','20150329_23:30:41_-0400','20150329_23:25:41_-0400'],
                                       "0-1dy: 1hr,1dy-1wk: 2hr, 1yr+: none",
                                       1427690151), [1427689541] )

if __name__ == '__main__':
    unittest.main()
