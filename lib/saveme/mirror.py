import sqlite3
from typing import List

# from .cfg import getdbdir as _cfg_database_directory
from .external import abspath, epoch2iso, getcurtime, indexer
from .types import Backup, ChecksumError, File
from .utils import StopException, TaskRunner, getcap


def indexpath(path: str) -> None:
    for file_path, _inode in indexer(path):
        try:
            print("%s/%s" % (path, file_path))  # S_ISDIR(res.st_mode),fp))
        except UnicodeEncodeError:
            print("%s/%r" % (path, file_path.encode("utf-8", "surrogateescape")))


def createdb() -> None:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    try:
        cur.execute("""drop table files""")
    except sqlite3.OperationalError:
        pass
    cur.execute(
        """
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
)"""
    )

    try:
        cur.execute("""drop table checksums""")
    except sqlite3.OperationalError:
        pass
    cur.execute(
        """
create table checksums (
    chksum text,
    volumeid integer,
    fileid text,
    gendate integer
)"""
    )
    try:
        cur.execute("""drop table archives""")
    except sqlite3.OperationalError:
        pass
    cur.execute(
        """
create table archives (
    path text unique,
    status text,
    capacity integer,
    chkdate integer
)"""
    )
    try:
        cur.execute("""drop table mirrors""")
    except sqlite3.OperationalError:
        pass
    cur.execute(
        """
create table mirrors (
    chksum text,
    archiveid integer
    blobchksum text,
    blobkey text,
    blobsize integer,
    copydate integer
)"""
    )
    try:
        cur.execute("""drop table volumes""")
    except sqlite3.OperationalError:
        pass
    cur.execute(
        """
create table volumes (
    path text,
    status text,
    createdate integer
)"""
    )
    conn.commit()
    cur.close()


def addbackup(volumeid: str, fileid: str, chksum: str) -> None:
    pass


def missingbackup(volumeid: int = None) -> None:
    checksums = findbackup(volumeid, withbackup=False)
    for chksum in checksums:
        print(
            "%s %s/%s"
            % (chksum.chksum, chksum.volume_path, chksum.file_path.decode("utf-8"))
        )


def findbackup(volumeid: int = None, withbackup: bool = True) -> List[Backup]:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    query = """select  checksums.chksum, volumes.path, files.path, mirrors.* from
               checksums join files on checksums.volumeid = files.volumeid and
               checksums.fileid=files.fileid join volumes on
               checksums.volumeid = volumes.rowid left join mirrors
               on checksums.chksum = mirrors.chksum where 1=1"""
    if not withbackup:
        query += " and mirrors.archiveid is null"
    if volumeid is not None:
        query += " and checksums.volumeid=%d" % volumeid
    cur.execute(query)
    checksums: List[Backup] = []
    for row in cur.fetchall():
        checksums += [Backup(*row)]
    cur.close()
    return checksums


def backupvolume(volumeid: int) -> int:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(
        """select rowid, path, status, createdate from volumes where rowid=%d"""
        % volumeid
    )
    volume = cur.fetchone()
    if volume is None:
        print("no volume with volumeid=%d" % volumeid)
        return 3
    volumeid, path, status, createdate = volume
    if status != "checksummed":
        print("will not work on this status")
        return 2
    return 0


def addsum(volumeid: int, fileid: str, chksum: str) -> None:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    print("inserting for %d, %s" % (volumeid, fileid))
    cur.execute(
        """insert into checksums values (?,?,?,?)""",
        (chksum, volumeid, fileid, getcurtime()),
    )
    conn.commit()
    cur.close()


def generatechecksum(path: str) -> str:
    runner = TaskRunner()
    runner.setvalue("path", path)
    runner.runstep("generate-checksum")
    if runner.getretcode() == 0:
        if runner.getout() != "":
            return runner.getout()
    raise ChecksumError()


def missingsum(volumeid: int = None) -> None:
    files = findsum(volumeid, withsum=False)
    for myfile in files:
        print(
            "%d %s %s/%s"
            % (
                myfile.volume_id,
                myfile.file_id,
                myfile.volume_path,
                myfile.file_path.decode("utf-8"),
            )
        )


def findsum(volumeid: int = None, withsum: bool = True) -> List[File]:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    query = """select files.volumeid, files.fileid, volumes.path, files.path from files
    left join checksums on files.fileid = checksums.fileid and files.volumeid=checksums.volumeid
    join volumes on files.volumeid=volumes.rowid
    where files.st_mode&32768"""
    if not withsum:
        query += " and checksums.chksum is null"
    if volumeid is not None:
        query += " and volumes.rowid=%d" % volumeid
    cur.execute(query)
    files: List[File] = []
    for row in cur.fetchall():
        files += [File(*row)]
    cur.close()
    return files


def checksumvolume(volumeid: int) -> int:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(
        """select rowid, path, status, createdate from volumes where rowid=%d"""
        % volumeid
    )
    volume = cur.fetchone()
    if volume is None:
        print("no volume with volumeid=%d" % volumeid)
        return 3
    volumeid, path, status, createdate = volume
    if status != "indexed":
        print("will not work on this status")
        return 2
    print("%d %12s %s %s" % (volumeid, status, epoch2iso(int(createdate)), path))
    files = []
    files = findsum(volumeid, withsum=False)
    for myfile in files:
        if myfile.volume_id != volumeid:
            print("this is odd %s" % (str(myfile)))
        chksum = generatechecksum(
            "%s/%s" % (myfile.volume_path, myfile.file_path.decode("utf-8"))
        )
        if chksum is None:
            print("err in chksum")
        else:
            addsum(myfile.volume_id, myfile.file_id, chksum)
    cur.execute(
        """update volumes set status='checksummed' where rowid=%d""" % (volumeid)
    )
    conn.commit()
    cur.close()
    return 0


def listarchives() -> None:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute("""select path, status, capacity, chkdate from archives""")
    for row in cur.fetchall():
        path, status, capacity, chkdate = row
        print(
            "%-24s %12s %s %10.2fGB"
            % (path, status, epoch2iso(int(chkdate)), capacity / 1e9)
        )
    cur.close()


def registerarchive(path: str) -> None:
    path = abspath(path)
    try:
        conn = sqlite3.connect("example.db")
        cur = conn.cursor()
        cur.execute(
            "insert into archives values (?,?,?,?)",
            (path, "online", getcap(path), getcurtime()),
        )
        conn.commit()
        cur.close()
    except StopException:
        print("Path is not a directory")
    except sqlite3.IntegrityError:
        print("There is already an archive with that name")


def listvolumes() -> None:
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute("""select rowid, path, status, createdate from volumes""")
    for row in cur.fetchall():
        rowid, path, status, createdate = row
        print("%d %12s %s %s" % (rowid, status, epoch2iso(int(createdate)), path))
    cur.close()


def index(path: str) -> int:
    path = abspath(path)
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()

    cur.execute("insert into volumes values (?,?,?)", (path, "indexed", getcurtime()))
    volumeid = cur.lastrowid
    try:
        for file_path, inode in indexer(path):
            fileid = "%d:%d" % (inode.st_dev, inode.st_ino)
            cur.execute(
                "insert into files values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    volumeid,
                    fileid,
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

    conn.commit()
    cur.close()
    return 0


# indexpath2("/home/toppk/androidbu/proc/10227/task/10259")
# indexpath("/t2/home/.snapshot/")
# indexpath2("/home")
# indexpath2("/home")
# indexpath2("/home/media/Shorts")
# [root@static tests]# more $( python3 -c "import os;os.sys.stdout.buffer.write
# (b'/home/toppk/crap/phonegames/s40game/
# Gameloft\xbe\xad\xb5\xe4\xd3\xce\xcf\xb7\xc8\xab\xbc\xaf/XIII/XIII.jad')" )
