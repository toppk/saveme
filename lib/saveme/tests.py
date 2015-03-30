import unittest
from main import CommandLine
cl=CommandLine()

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
        import pdb
        #pdb.set_trace()
        self.assertEqual(self.__class__._culltimeline(['20150329_23:35:41_-0400'],
                                             "0-1dy: all, 1dy-1wk: 4hr, 1wk-3mo: 1wk, 3mo+: 1mo",
                                             1427690141), [] )

if __name__ == '__main__':
    unittest.main()
