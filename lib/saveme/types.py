from typing import List, NamedTuple, Optional, Union


class ChecksumError(Exception):
    pass


class StopException(Exception):
    pass


class MissingParamException(Exception):
    pass


class Routine:
    def __init__(self, script: str, args: List[str], generates_commands: bool) -> None:
        self.script = script
        self.args = args
        self.generates_commands = generates_commands

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(script={self.script}, args={self.args}, generates_commands={self.generates_commands})"


class SnapPolicy(NamedTuple):
    start: int
    end: Optional[int]
    sparseness: Union[str, int]
    rule: str


class Backup(NamedTuple):
    chksum: str
    volume_path: str
    file_path: bytes


class File(NamedTuple):
    volume_id: int
    file_id: str
    volume_path: str
    file_path: bytes
