#!/usr/bin/env python3

import os
import sys
import time
import unittest
from pathlib import Path

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
        from saveme.external import parsedate
        from saveme.snapshots import culltimeline

        self._parsedate = parsedate
        self._culltimeline = culltimeline

    def test_util_parsedate(self):
        # date +"%Y-%m-%dT%H:%M:%S%z"
        self.assertEqual(self._parsedate("2015-04-06T23:05:04-0400"), 1428375904000000)

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


class TestDST(unittest.TestCase):
    # America/New_York: 2026-03-08 springs forward, 2026-11-01 falls back
    POLICY = "0-1dy: all, 1dy-1wk: 8hr, 1wk+: none"
    NOW = 1793794200 * 1000000  # 2026-11-04T12:10:00Z

    def setUp(self):
        self._tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/New_York"
        time.tzset()

    def tearDown(self):
        if self._tz is None:
            del os.environ["TZ"]
        else:
            os.environ["TZ"] = self._tz
        time.tzset()

    @staticmethod
    def _name(epoch: int) -> str:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        thedate = datetime.fromtimestamp(epoch, ZoneInfo("America/New_York"))
        return thedate.strftime("%Y-%m-%dT%H:%M:%S%z")

    def test_parsedate_dst(self):
        from saveme.external import parsedate

        self.assertEqual(parsedate("2026-11-01T01:30:00-0400"), 1793511000000000)
        self.assertEqual(parsedate("2026-11-01T01:15:00-0500"), 1793513700000000)
        self.assertEqual(parsedate("2026-03-08T01:59:00-0500"), 1772953140000000)
        self.assertEqual(parsedate("2026-03-08T03:01:00-0400"), 1772953260000000)

    def test_epoch2iso_dst(self):
        from saveme.external import epoch2iso, parsedate

        self.assertEqual(epoch2iso(1793511000000000), "2026-11-01T01:30:00-0400")
        self.assertEqual(epoch2iso(1793513700000000), "2026-11-01T01:15:00-0500")
        self.assertEqual(epoch2iso(1772953260000000), "2026-03-08T03:01:00-0400")
        for epoch in (1793511000000000, 1793513700000000, 1772953140000000):
            self.assertEqual(parsedate(epoch2iso(epoch)), epoch)

    def test_cull_order_across_dst(self):
        from saveme.snapshots import culltimeline

        # the -0500 one is 45 minutes later, though its clock time is earlier
        snaps = ["2026-11-01T01:15:00-0500", "2026-11-01T01:30:00-0400"]
        self.assertEqual(
            culltimeline(snaps, "0+: 1hr", self.NOW), ["2026-11-01T01:15:00-0500"]
        )

    def test_cull_age_uses_offset(self):
        from saveme.snapshots import culltimeline

        snap = "2026-11-01T01:15:00-0500"
        now = (1793513700 + 20 * 3600) * 1000000
        self.assertEqual(culltimeline([snap], "0-1dy: all, 1dy+: none", now), [])

    def test_cull_spacing_from_last_kept(self):
        from saveme.external import parsedate
        from saveme.snapshots import culltimeline

        end = self.NOW // 1000000 - 600
        snaps = [self._name(t) for t in range(end - 8 * 86400, end + 1, 1800)]
        culled = set(culltimeline(snaps, self.POLICY, self.NOW))
        kept = sorted(parsedate(s) for s in snaps if s not in culled)
        day, week = 86400 * 1000000, 7 * 86400 * 1000000
        sparse = [t for t in kept if day <= self.NOW - t < week]
        gaps = {b - a for a, b in zip(sparse, sparse[1:])}
        self.assertEqual(len(sparse), 18)
        self.assertEqual(gaps, {8 * 3600 * 1000000})
        self.assertTrue(all(self.NOW - t < week for t in kept))
        self.assertEqual(len([t for t in kept if self.NOW - t < day]), 48)


class TestPolicyBoundaries(unittest.TestCase):
    SNAP = "2026-11-01T01:15:00-0500"
    DAY = 86400 * 1000000

    def setUp(self):
        from saveme.external import parsedate
        from saveme.snapshots import culltimeline

        self._cull = culltimeline
        self._at = parsedate(self.SNAP)

    def test_boundary_belongs_to_later_range(self):
        now = self._at + self.DAY
        self.assertEqual(self._cull([self.SNAP], "0-1dy: none, 1dy+: all", now), [])
        self.assertEqual(
            self._cull([self.SNAP], "0-1dy: all, 1dy+: none", now), [self.SNAP]
        )

    def test_boundary_deleted_once(self):
        now = self._at + self.DAY
        self.assertEqual(
            self._cull([self.SNAP], "0-1dy: none, 1dy+: none", now), [self.SNAP]
        )

    def test_exact_interval_is_kept(self):
        later = "2026-11-01T09:15:00-0500"
        now = self._at + self.DAY
        self.assertEqual(self._cull([self.SNAP, later], "0+: 8hr", now), [])

    def test_manage_skips_delete_when_nothing_culled(self):
        from unittest import mock

        from saveme import snapshots

        runner = mock.MagicMock()
        runner.getretcode.return_value = 0
        runner.getout.return_value = self.SNAP
        with mock.patch.object(snapshots, "TaskRunner", return_value=runner):
            with mock.patch.object(snapshots, "getcurtime", return_value=self._at):
                self.assertEqual(snapshots.manage("/t", "0+: all", False), 0)
        steps = [c.args[0] for c in runner.runstep.call_args_list]
        self.assertEqual(steps, ["list-snap"])


class TestExitCodes(unittest.TestCase):
    SNAP = "2026-01-01T00:00:00-0500"

    def _run(self, results, func, *args, answer=None, **kwargs):
        from unittest import mock

        from saveme import snapshots, utils

        calls = []

        def fake(args, stdin=None):
            calls.append(args)
            return results[len(calls) - 1]

        with mock.patch.object(utils, "runcommand", side_effect=fake):
            with mock.patch("builtins.input", return_value=answer):
                with mock.patch.object(
                    snapshots, "getcurtime", return_value=1893456000 * 1000000
                ):
                    return getattr(snapshots, func)(*args, **kwargs), len(calls)

    def test_create_ok(self):
        res = [(0, "btrfs subvolume snapshot\n", ""), (0, "", "")]
        self.assertEqual(self._run(res, "create", "/x", promptuser=False), (0, 2))

    def test_create_commands_fail(self):
        res = [(0, "btrfs subvolume snapshot\n", ""), (1, "", "boom\n")]
        self.assertEqual(self._run(res, "create", "/x", promptuser=False), (1, 2))

    def test_create_script_fails(self):
        res = [(3, "", "not a btrfs path\n")]
        self.assertEqual(self._run(res, "create", "/x", promptuser=False), (3, 1))

    def test_create_declined(self):
        res = [(0, "btrfs subvolume snapshot\n", "")]
        self.assertEqual(self._run(res, "create", "/x", answer="n"), (2, 1))

    def test_manage_deletes_ok(self):
        res = [
            (0, self.SNAP + "\n", ""),
            (0, "btrfs subvolume delete\n", ""),
            (0, "", ""),
        ]
        policy = "0-1dy: all, 1dy+: none"
        self.assertEqual(
            self._run(res, "manage", "/x", policy, promptuser=False), (0, 3)
        )

    def test_list_script_fails(self):
        res = [(1, "", "/x not a directory\n")]
        self.assertEqual(self._run(res, "listsnapshot", "/x"), (1, 1))


class TestInstallLayout(unittest.TestCase):
    REPO = Path(__file__).resolve().parents[1]

    def test_scriptsdir_from_package(self):
        from saveme.cfg import getscriptsdir

        self.assertEqual(getscriptsdir(), str(self.REPO / "scripts"))
        self.assertTrue((Path(getscriptsdir()) / "ssfs-list-snap.sh").is_file())

    def test_tools_through_symlink(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            evil = Path(tmp, "evil", "saveme")
            evil.mkdir(parents=True)
            for name in ("__init__.py", "api.py"):
                (evil / name).write_text('print("HOSTILE")\nraise SystemExit(99)\n')
            sbin = Path(tmp, "sbin")
            sbin.mkdir()
            env = dict(os.environ, PYTHONPATH=str(evil.parent))
            for tool, args, code in (
                ("snapmgr", ["list", "/nonexistent-saveme-path"], 1),
                ("disktool", [], 12),
                ("mirroradm", [], 1),
            ):
                (sbin / tool).symlink_to(self.REPO / "tools" / tool)
                proc = subprocess.run(
                    [str(sbin / tool), *args],
                    cwd=tmp,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc.returncode, code, proc.stdout + proc.stderr)
                self.assertNotIn("HOSTILE", proc.stdout)
                self.assertNotIn("Traceback", proc.stderr)
                self.assertIn("usage:" if not args else "not a directory", proc.stdout)


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
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
    unittest.main()
