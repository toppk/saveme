
#
#
#
#from .cfg import getdbdir as _cfg_database_directory
from .external import getcurtime, indexer, epoch2iso, abspath
from .utils import TaskRunner, getcap, StopException

import sqlite3

#

def indexpath(path):
    for file in indexer(path):
        try:
            print("%s/%s" % (path, file[0])) # S_ISDIR(res.st_mode),fp))
        except UnicodeEncodeError:
            print("%s/%s" % (path, file[0].encode('utf-8', 'surrogateescape')))

def createdb():
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    try:
        cur.execute('''drop table files''')
    except sqlite3.OperationalError:
        pass
    cur.execute('''
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
)''')

    try:
        cur.execute('''drop table checksums''')
    except sqlite3.OperationalError:
        pass
    cur.execute('''
create table checksums (
    chksum text, 
    volumeid integer,
    fileid text, 
    gendate integer
)''')
    try:
        cur.execute('''drop table archives''')
    except sqlite3.OperationalError:
        pass
    cur.execute('''
create table archives (
    path text unique, 
    status text,
    capacity integer,
    chkdate integer
)''')
    try:
        cur.execute('''drop table mirrors''')
    except sqlite3.OperationalError:
        pass
    cur.execute('''
create table mirrors (
    chksum text, 
    archiveid integer
    blobchksum text, 
    blobkey text,
    blobsize integer,
    copydate integer
)''')
    try:
        cur.execute('''drop table volumes''')
    except sqlite3.OperationalError:
        pass
    cur.execute('''
create table volumes (
    path text, 
    status text,
    createdate integer
)''')
    conn.commit()
    cur.close()

def addsum(volumeid, fileid, chksum):
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    print("inserting for %d, %s"%(volumeid, fileid))
    cur.execute('''insert into checksums values (?,?,?,?)''',
                (chksum, volumeid, fileid, getcurtime()))
    conn.commit()
    cur.close()

def checksumvolume(volumeid):
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    cur.execute('''select rowid, path, status, createdate from volumes where rowid=%d'''%volumeid)
    volume = cur.fetchone()
    if volume is None:
        print("no volume with volumeid=%d"%volumeid)
        return 3
    volumeid, path, status, createdate = volume
    if status != "indexed":
        print("will not work on this status")
        return 2
    print('%d %12s %s %s' % (volumeid, status, epoch2iso(int(createdate)), path))
    files = []
    files = findsum(volumeid, withsums=False)
    for file in files:
        if file[0] != volumeid:
            print("this is odd %s" % (str(file)))
        chksum = generatechecksum("%s/%s"%(file[2], file[3].decode('utf-8')))
        if chksum is None:
            print("errir in chksum")
        else:
            addsum(file[0], file[1], chksum)
    cur.execute('''update volumes set status='checksumed' where rowid=%d'''%(volumeid))
    conn.commit()
    cur.close()

def generatechecksum(path):

    runner = TaskRunner()
    runner.setvalue('path', path)
    runner.runstep("generate-checksum")
    if runner.getretcode() == 0:
        if runner.getout() != "":
            return runner.getout()

def listvolumes():
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    cur.execute('''select rowid, path, status, createdate from volumes''')
    for row in cur.fetchall():
        rowid, path, status, createdate = row
        print('%d %12s %s %s' % (rowid, status, epoch2iso(int(createdate)), path))
    cur.close()

def missingsum(volumeid=None):
    files = findsum(volumeid, withsums=False)
    for file in files:
        print('%d %s %s/%s' % (file[0], file[1], file[2], file[3].decode('utf-8')))

def findsum(volumeid=None, withsums=True):
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()
    query = '''select files.volumeid, files.fileid, volumes.path, files.path from files
    left join checksums on files.fileid = checksums.fileid and files.volumeid=checksums.volumeid
    join volumes on files.volumeid=volumes.rowid
    where files.st_mode&32768'''
    if not withsums:
        query += ' and checksums.chksum is null'
    if volumeid is not None:
        query += " and volumes.rowid=%d" % volumeid
    cur.execute(query)
    files = []
    for row in cur.fetchall():
        files += [row]
    cur.close()
    return files

def registerarchive(path):
    path = abspath(path)
    try:
        conn = sqlite3.connect('example.db')
        cur = conn.cursor()
        cur.execute('insert into archives values (?,?,?,?)',
                    (path, 'online', getcap(path), getcurtime()))
        conn.commit()
        cur.close()
    except StopException as err:
        print("Path is not a directory")
    except sqlite3.IntegrityError as err:
        print("There is already an archive with that name")
    
def index(path):
    path = abspath(path)
    conn = sqlite3.connect('example.db')
    cur = conn.cursor()

    cur.execute('insert into volumes values (?,?,?)',
                (path, 'indexed', getcurtime()))
    volumeid = cur.lastrowid
    try:
        for file in indexer(path):
            inode = file[1]
            fileid = "%d:%d" % (inode.st_dev, inode.st_ino)
            cur.execute('insert into files values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (volumeid, fileid, file[0].encode('utf8', 'surrogateescape'),
                         inode.st_uid, inode.st_gid, int(inode.st_atime_ns/1e3),
                         int(inode.st_ctime_ns/1e3), int(inode.st_mtime_ns/1e3),
                         inode.st_blksize, inode.st_blocks, inode.st_size,
                         inode.st_rdev, inode.st_dev, inode.st_ino, inode.st_mode,
                         inode.st_nlink))
    except ValueError as err:
        print("cannot index due to issue[%s] "%err)
        return 1


    conn.commit()
    cur.close()
    return 0

#indexpath2("/home/toppk/androidbu/proc/10227/task/10259")
#indexpath("/t2/home/.snapshot/")
#indexpath2("/home")
#indexpath2("/home")
#indexpath2("/home/media/Shorts")
#[root@static tests]# more $( python3 -c "import os;os.sys.stdout.buffer.write(b'/home/toppk/crap/phonegames/s40game/Gameloft\xbe\xad\xb5\xe4\xd3\xce\xcf\xb7\xc8\xab\xbc\xaf/XIII/XIII.jad')" )
