#!/usr/bin/env python3

import sys
import unittest

print(" Running Python Version [%s] " % sys.version)


class TestMain(unittest.TestCase):
    def setUp(self):
        from saveme.api import CommandLine

        self._cl = CommandLine()

    def test_cli_go(self):
        self.assertEqual(self._cl.snapmgr(["me"]), 12)

    def test_cli_help(self):
        self.assertEqual(self._cl.help(), True)


class TestUtil(unittest.TestCase):

    _parsedate = None

    def setUp(self):
        from saveme.snapshots import culltimeline
        from saveme.external import parsedate

        self._parsedate = parsedate
        self._culltimeline = culltimeline

    def test_util_parsedate(self):
        # date +"%Y-%m-%dT%H:%M:%S%z"
        self.assertEqual(self._parsedate("2015-04-06T23:05:04-0400"), 1428361508000000)

    def test_util_culltimeline(self):
        # date +"%Y-%m-%dT%H:%M:%S%z"
        from saveme.snapshots import culltimeline as _culltimeline

        # pdb.set_trace()
        self.assertEqual(
            _culltimeline(
                ["2015-04-06T23:05:04-0400"],
                "0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none",
                1428376600000000,
            ),
            [],
        )
        self.assertEqual(
            _culltimeline(
                [
                    "2015-01-06T23:05:04-0400",
                    "2015-02-06T23:05:04-0400",
                    "2015-03-06T23:05:04-0400",
                ],
                "0-1dy: all, 1dy-1wk: 4hr, 1wk-12wk: 1wk, 12wk-1yr: 4wk, 1yr+: none",
                1428376600000000,
            ),
            [],
        )
        self.assertEqual(
            _culltimeline(
                [
                    "2015-04-06T23:15:04-0400",
                    "2015-04-06T23:10:04-0400",
                    "2015-04-06T23:05:04-0400",
                ],
                "0-1dy: 1hr,1dy-1wk: 2hr, 1yr+: none",
                1428376600000000,
            ),
            ["2015-04-06T23:15:04-0400", "2015-04-06T23:10:04-0400"],
        )

        self.assertEqual(
            _culltimeline(
                [
                    "2015-04-04T23:05:04-0400",
                    "2015-04-06T23:10:04-0400",
                    "2015-04-06T23:05:04-0400",
                ],
                "0-1yr: 1dy",
                1428376600000000,
            ),
            ["2015-04-06T23:10:04-0400"],
        )


class TestExternal(unittest.TestCase):
    def setUp(self):
        pass

    def test_external_runcommand(self):
        from saveme.external import runcommand as _runcommand

        self.assertEqual(
            _runcommand(["/bin/bash", "-c", "echo stdout\necho stderr 1>&2\nexit 3"]),
            (3, "stdout\n", "stderr\n"),
        )

    def test_external_runcommand_stdin(self):
        from saveme.external import runcommand as _runcommand

        self.assertEqual(
            _runcommand(
                ["/bin/bash", "-c", "tac\necho stderr 1>&2\nexit 3"],
                stdin="stdin\nfrom\n",
            ),
            (3, "from\nstdin\n", "stderr\n"),
        )


if __name__ == "__main__":
    import sys
    import os

    sys.path += [os.path.abspath(os.path.dirname(sys.argv[0]) + "/../lib")]
    unittest.main()
