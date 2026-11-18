import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator, List

from .cfg import getdbdir
from .external import abspath, epoch2iso, getcurtime, indexer
from .types import Backup, ChecksumError, File, NoDatabase
from .utils import StopException, TaskRunner, getcap


def _connect() -> sqlite3.Connection:
    dbdir = Path(getdbdir())
    if not dbdir.is_dir():
        raise NoDatabase(str(dbdir))
    return sqlite3.connect(dbdir / "mirror.db")


@contextmanager
def _db() -> Iterator[sqlite3.Cursor]:
    # commits on success, rolls back on error, always closes
    with closing(_connect()) as conn, conn, closing(conn.cursor()) as cur:
        yield cur


def indexpath(path: str) -> None:
    for file_path, _inode in indexer(path):
        try:
            print("%s/%s" % (path, file_path))  # S_ISDIR(res.st_mode),fp))
        except UnicodeEncodeError:
            print("%s/%r" % (path, file_path.encode("utf-8", "surrogateescape")))


def createdb() -> None:
    with _db() as cur:
        for table in ("files", "checksums", "archives", "mirrors", "volumes"):
            cur.execute("drop table if exists " + table)
        _createtables(cur)


def _createtables(cur: sqlite3.Cursor) -> None:
    cur.execute("""
create table files (
    volumeid integer,
    fileid text,
    path text,
    st_uid integer,
    st_gid integer,
    st_atime integer,
    st_ctime integer,
    st_mtime integer,
    st_blksize integer,
    st_blocks integer,
    st_size integer,
    st_rdev integer,
    st_dev integer,
    st_ino integer,
    st_mode integer,
    st_nlink integer
)""")
    cur.execute("""
create table checksums (
    chksum text,
    volumeid integer,
    fileid text,
    gendate integer
)""")
    cur.execute("""
create table archives (
    path text unique,
    status text,
    capacity integer,
    chkdate integer
)""")
    cur.execute("""
create table mirrors (
    chksum text,
    archiveid integer,
    blobchksum text,
    blobkey text,
    blobsize integer,
    copydate integer
)""")
    cur.execute("""
create table volumes (
    path text,
    status text,
    createdate integer
)""")


def addbackup(
    chksum: str, archiveid: int, blobchksum: str, blobkey: str, blobsize: int
) -> None:
    with _db() as cur:
        cur.execute(
            "insert into mirrors values (?,?,?,?,?,?)",
            (chksum, archiveid, blobchksum, blobkey, blobsize, getcurtime()),
        )


def missingbackup(volumeid: int | None = None) -> None:
    for backup in findbackup(volumeid, withbackup=False):
        print(
            "%s %s/%s"
            % (backup.chksum, backup.volume_path, backup.file_path.decode("utf-8"))
        )


def findbackup(volumeid: int | None = None, withbackup: bool = True) -> List[Backup]:
    query = """select checksums.chksum, volumes.path, files.path from
               checksums join files on checksums.volumeid = files.volumeid and
               checksums.fileid = files.fileid join volumes on
               checksums.volumeid = volumes.rowid left join mirrors
               on checksums.chksum = mirrors.chksum where 1=1"""
    params: List[int] = []
    if not withbackup:
        query += " and mirrors.archiveid is null"
    if volumeid is not None:
        query += " and checksums.volumeid = ?"
        params.append(volumeid)
    with _db() as cur:
        cur.execute(query, params)
        return [Backup(*row) for row in cur.fetchall()]


def _volume(cur: sqlite3.Cursor, volumeid: int) -> tuple | None:
    cur.execute(
        "select rowid, path, status, createdate from volumes where rowid = ?",
        (volumeid,),
    )
    return cur.fetchone()


def backupvolume(volumeid: int) -> int:
    with _db() as cur:
        volume = _volume(cur, volumeid)
    if volume is None:
        print("no volume with volumeid=%d" % volumeid)
        return 3
    if volume[2] != "checksummed":
        print("will not work on this status")
        return 2
    return 0


def addsum(volumeid: int, fileid: str, chksum: str) -> None:
    print("inserting for %d, %s" % (volumeid, fileid))
    with _db() as cur:
        cur.execute(
            "insert into checksums values (?,?,?,?)",
            (chksum, volumeid, fileid, getcurtime()),
        )


def generatechecksum(path: str) -> str:
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.runstep("generate-checksum")
    if runner.getretcode() == 0:
        if runner.getout() != "":
            return runner.getout()
    raise ChecksumError()


def missingsum(volumeid: int | None = None) -> None:
    for myfile in findsum(volumeid, withsum=False):
        print(
            "%d %s %s/%s"
            % (
                myfile.volume_id,
                myfile.file_id,
                myfile.volume_path,
                myfile.file_path.decode("utf-8"),
            )
        )


def findsum(volumeid: int | None = None, withsum: bool = True) -> List[File]:
    query = """select files.volumeid, files.fileid, volumes.path, files.path from files
    left join checksums on files.fileid = checksums.fileid and files.volumeid = checksums.volumeid
    join volumes on files.volumeid = volumes.rowid
    where files.st_mode & 32768"""
    params: List[int] = []
    if not withsum:
        query += " and checksums.chksum is null"
    if volumeid is not None:
        query += " and volumes.rowid = ?"
        params.append(volumeid)
    with _db() as cur:
        cur.execute(query, params)
        return [File(*row) for row in cur.fetchall()]


def checksumvolume(volumeid: int) -> int:
    with _db() as cur:
        volume = _volume(cur, volumeid)
    if volume is None:
        print("no volume with volumeid=%d" % volumeid)
        return 3
    volumeid, path, status, createdate = volume
    if status != "indexed":
        print("will not work on this status")
        return 2
    print("%d %12s %s %s" % (volumeid, status, epoch2iso(int(createdate)), path))
    for myfile in findsum(volumeid, withsum=False):
        chksum = generatechecksum(
            "%s/%s" % (myfile.volume_path, myfile.file_path.decode("utf-8"))
        )
        addsum(myfile.volume_id, myfile.file_id, chksum)
    with _db() as cur:
        cur.execute(
            "update volumes set status = 'checksummed' where rowid = ?", (volumeid,)
        )
    return 0


def listarchives() -> None:
    with _db() as cur:
        cur.execute("select path, status, capacity, chkdate from archives")
        rows = cur.fetchall()
    for path, status, capacity, chkdate in rows:
        print(
            "%-24s %12s %s %10.2fGB"
            % (path, status, epoch2iso(int(chkdate)), capacity / 1e9)
        )


def registerarchive(path: str) -> None:
    path = abspath(path)
    try:
        with _db() as cur:
            cur.execute(
                "insert into archives values (?,?,?,?)",
                (path, "online", getcap(path), getcurtime()),
            )
    except StopException:
        print("Path is not a directory")
    except sqlite3.IntegrityError:
        print("There is already an archive with that name")


def listvolumes() -> None:
    with _db() as cur:
        cur.execute("select rowid, path, status, createdate from volumes")
        rows = cur.fetchall()
    for rowid, path, status, createdate in rows:
        print("%d %12s %s %s" % (rowid, status, epoch2iso(int(createdate)), path))


def index(path: str) -> int:
    path = abspath(path)
    try:
        with _db() as cur:
            cur.execute(
                "insert into volumes values (?,?,?)", (path, "indexed", getcurtime())
            )
            volumeid = cur.lastrowid
            for file_path, inode in indexer(path):
                cur.execute(
                    "insert into files values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        volumeid,
                        "%d:%d" % (inode.st_dev, inode.st_ino),
                        file_path.encode("utf8", "surrogateescape"),
                        inode.st_uid,
                        inode.st_gid,
                        int(inode.st_atime_ns / 1e3),
                        int(inode.st_ctime_ns / 1e3),
                        int(inode.st_mtime_ns / 1e3),
                        inode.st_blksize,
                        inode.st_blocks,
                        inode.st_size,
                        inode.st_rdev,
                        inode.st_dev,
                        inode.st_ino,
                        inode.st_mode,
                        inode.st_nlink,
                    ),
                )
    except ValueError as err:
        print("cannot index due to issue[%s] " % err)
        return 1
    return 0
