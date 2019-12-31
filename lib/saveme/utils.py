import re
from typing import Dict, List, Optional, Tuple, Union

from .cfg import getscriptsdir as _cfg_scripts_directory
from .external import runcommand
from .schema import findscript
from .types import MissingParamException, SnapPolicy, StopException


class TaskRunner:
    def __init__(self) -> None:
        self._dict: Dict[str, str] = {}
        self._alias: Dict[str, str] = {}
        self._output: Optional[str] = None
        self._retcode: Optional[int] = None

    def getretcode(self) -> int:
        assert isinstance(self._retcode, int)
        return self._retcode

    def setvalue(self, key: str, value: str) -> None:
        self._dict[key] = value

    def addalias(self, origkey: str, alias: str) -> None:
        self._alias[alias] = origkey

    def getvalue(self, alias: str) -> str:
        if alias in self._alias:
            alias = self._alias[alias]

        return self._dict[alias]

    def dump(self) -> None:
        for key, value in self._dict.items():
            print("  Key=%s => Value=%s" % (key, value))
        for key, value in self._alias.items():
            print("  Alias=%s => Origkey=%s" % (key, value))

    def getout(self) -> str:
        assert isinstance(self._output, str)
        return self._output

    def runstep(
        self,
        step: str,
        options: List[Tuple[str, str]] = None,
        stdin: str = None,
        promptuser: bool = True,
    ) -> int:
        action = findscript(step)
        # print("action[%s]: %s with [%s] that is a cmdgen=%s" %
        #      (step, action['script'], action['args'],
        #       action['generates-commands']))
        args = ["/bin/bash", "%s/%s" % (_cfg_scripts_directory(), action.script)]
        for arg in action.args:
            if arg not in self._dict and arg not in self._alias:
                raise MissingParamException("Cannot find %s in dict" % arg)
            args += [self.getvalue(arg)]

        if options is not None:
            for option in options:
                args += ["--%s=%s" % (option[0], option[1])]

        retcode, out, err = runcommand(args, stdin=stdin)
        self._retcode = retcode
        self._output = out.strip()
        if retcode == 0:
            for line in out.split("\n"):
                regex = re.compile(r"#\s+'(\S+)':'(\S+)'")
                match = regex.match(line)
                if match is not None:
                    self._dict[match.group(1)] = match.group(2)
            if action.generates_commands:
                if out == "":
                    print("NO ACTION GENERATED")
                self._retcode = launch(out, promptuser=promptuser)
        else:
            print("FAILURE - %s issues [%s][%s][%d]" % (step, out, err, retcode))
            raise StopException()
        return retcode


def launch(cmds: str, promptuser: bool = True) -> bool:
    if promptuser:
        print(
            """SUGGESTED ACTION
---
%s
---"""
            % "\n".join([i for i in cmds.split("\n") if i != "" and i[0] != "#"])
        )
        response = input("==> Do you wish to launch? y/n ")
        if response != "y":
            raise StopException()
    else:
        print(
            """LAUNCHING THE FOLLOWING ACTION
---
%s
---"""
            % "\n".join([i for i in cmds.split("\n") if i != "" and i[0] != "#"])
        )

    if not promptuser or response == "y":
        args = ["/bin/bash", "-e", "-c", cmds]
        retcode, out, err = runcommand(args)
        if retcode == 0:
            print("SUCCESS -  Output is below:\n---\n%s---" % out)
        else:
            print("ERROR - out,err,exit [%s][%s][%d]" % (out, err, retcode))
            return False
    return True


def getcap(path: str) -> int:
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.runstep("get-filesystem-capacity")
    return int(runner.getvalue("capacity"))


def parsepolicy(policystr: str) -> List[SnapPolicy]:
    rules: List[SnapPolicy] = []
    for rule in policystr.split(","):
        rule = rule.strip()
        (rangespec, sparse) = rule.split(":")
        sparse = sparse.strip()
        rangespec = rangespec.strip()
        start = None
        end = None
        sparseness: Union[str, int] = sparse if sparse in (
            "all",
            "none",
        ) else parsehdate(sparse)
        if rangespec.find("-") > 0:
            start, end = [parsehdate(hdate) for hdate in rangespec.split("-")]
        elif rangespec.endswith("+"):
            start = parsehdate(rangespec[:-1])
        else:
            raise ValueError("this is bad")
        if end is not None and start > end:
            raise ValueError(
                "cannot end before you start %s - %s[%s]" % (start, end, rangespec)
            )
        rules += [SnapPolicy(start, end, sparseness, rule)]

    # need to sort and quality check the rules (and fill any gaps)
    return rules


def parsehdate(timestr: str) -> int:
    # no mo(nth) as there isn't a time definition of a month.
    time = None
    timestr = timestr.strip()
    if timestr == "0":
        time = 0
    elif timestr.endswith("yr"):
        time = int(int(timestr[:-2]) * 365 * 24 * 60 * 60 * 1e6)
    elif timestr.endswith("mo"):
        # I said no month
        raise ValueError("no mo(nth) support")
    elif timestr.endswith("wk"):
        time = int(int(timestr[:-2]) * 7 * 24 * 60 * 60 * 1e6)
    elif timestr.endswith("dy"):
        time = int(int(timestr[:-2]) * 24 * 60 * 60 * 1e6)
    elif timestr.endswith("hr"):
        time = int(int(timestr[:-2]) * 60 * 60 * 1e6)
    elif timestr.endswith("mi"):
        time = int(int(timestr[:-2]) * 60 * 1e6)
    elif timestr.endswith("se"):
        time = int(int(timestr[:-2]) * 1e6)
    else:
        raise ValueError("bad time spec %s" % timestr)
    return time
