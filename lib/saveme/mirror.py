
#
#
#
from .cfg import getdbdir as _cfg_database_directory
from .external import getcurtime
import scandir
import queue
import locale
import os, sys
from stat import S_ISDIR
import sqlite3

#

def indexpath(path):
    print("supposed to index %s to %s" % (path, _cfg_database_directory()))

    q = queue.Queue()
    locale.setlocale(locale.LC_CTYPE, 'en_US')
    for de in scandir.scandir(path=path):
        q.put(de)

    _mylocale = locale.setlocale(locale.LC_CTYPE)
    locale.setlocale(locale.LC_CTYPE, 'en_US.iso88591')
    locale.setlocale(locale.LC_CTYPE, 'ascii')
    while not q.empty():
        de = q.get()
        print("found %s + %s" % (de.path, de.name))
        if de.is_dir():
          #  print ("adding %s + %s" % (de.path,de.name ))
            entries = []
            try:
                entries = scandir.scandir(path=de.path)
            except UnicodeDecodeError as e:
                print("swigint to windows %s" % e)
                locale.setlocale(locale.LC_CTYPE, 'en_US.iso88591')
                entries = scandir.scandir(path=de.path)
                locale.setlocale(locale.LC_CTYPE, _mylocale)
            for de in entries:
                try:
                    q.put(de)
                except UnicodeDecodeError as e:
                    locale.setlocale(locale.LC_CTYPE, 'en_US.iso88591')
                    q.put(de)
                    locale.setlocale(locale.LC_CTYPE, _mylocale)

        #print ("%s (%s) [%s]" % (de.path,dir(de),de.stat() ))

def indexpath2(path):
    for file in indexer(path):
        try:
            print("%/%s" % (path, file[0])) # S_ISDIR(res.st_mode),fp))
        except UnicodeEncodeError:
            print("%s/%s" % (path, file[0].encode('utf-8', 'surrogateescape')))

def indexer(path):
    #print("supposed to index %s to %s" % (path,_cfg_database_directory()))
    if path[-1] != "/":
        path += "/"
    print(path)
    yield ('.', os.lstat(path))
    q = queue.Queue()
    q.put(path)
    while not q.empty():
        entry = q.get()
        for fn in os.listdir(entry):
            fp = "%s%s" % (entry, fn)
            res = os.lstat(fp)
            if S_ISDIR(res.st_mode):
                q.put(fp+'/')
            yield (fp[len(path):], res)
#            try:
#                #print("%s" % (fp)) # S_ISDIR(res.st_mode),fp))
#                yield (fp,locale.setlocale(locale.LC_CTYPE))
#            except UnicodeEncodeError:
#                #print( fp.encode('utf8','surrogateescape') )
#                yield (fp.encode('utf8','surrogateescape'),'binary')

def createdb():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    try:
        c.execute('''drop table files''')
    except sqlite3.OperationalError:
        pass
    c.execute('''create table files
    (volumeid integer, fileid text, path text, st_uid integer, st_gid integer,
    st_atime integer, st_ctime integer, st_mtime integer,
    st_blksize integer, st_blocks integer, st_size integer,
    st_rdev integer, st_dev integer, st_ino integer,
    st_mode integer, st_nlink integer)''')
    # st_atime', 'st_atime_ns', 'st_blksize', 'st_blocks', 'st_ctime', 'st_ctime_ns', 'st_dev', 'st_gid', 'st_ino', 'st_mode', 'st_mtime', 'st_mtime_ns', 'st_nlink', 'st_rdev', 'st_size', 'st_uid
    try:
        c.execute('''drop table checksums''')
    except sqlite3.OperationalError:
        pass
    c.execute('''create table checksums
    (chksum text, fileid text, volumeid text)''')
    try:
        c.execute('''drop table volumes''')
    except sqlite3.OperationalError:
        pass
    c.execute('''create table volumes
    (path text, status text, created integer)''')
    conn.commit()
    c.close()

def addsum(volumeid, fileid, chksum):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''insert into checksums values (?,?,?)''',(chksum,fileid,int(volumeid)))
    conn.commit()
    c.close()
    
def missingsum():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''select files.path, files.fileid, files.volumeid, volumes.path from files 
    left join checksums on files.fileid = checksums.fileid and files.volumeid=checksums.volumeid
    join volumes on files.volumeid=volumes.rowid 
    where files.st_mode&32768 and checksums.chksum is null''')
    for row in c.fetchall():
        filepath, fileid, volumeid, volpath = row
        print('%d %s %s/%s' % (volumeid, fileid, volpath, filepath.decode('utf-8')))

    

def index(path):
    if not os.path.isdir(path):
        print("path %s is not a directory"%path)
        return 2

    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    c.execute('insert into volumes values (?,?,?)',(path, 'indexed', getcurtime()))
    volumeid = c.lastrowid

    for f in indexer(path):
        inode =  f[1]
        fileid = "%d:%d" % (inode.st_dev, inode.st_ino)
        c.execute('insert into files values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (volumeid, fileid, f[0].encode('utf8', 'surrogateescape'), inode.st_uid,
                   inode.st_gid, int(inode.st_atime_ns/1e3), int(inode.st_ctime_ns/1e3),
                   int(inode.st_mtime_ns/1e3), inode.st_blksize,
                   inode.st_blocks, inode.st_size, inode.st_rdev,
                   inode.st_dev, inode.st_ino, inode.st_mode,
                   inode.st_nlink))

        
    conn.commit()
    c.close()

#indexpath2("/home/toppk/androidbu/proc/10227/task/10259")

#indexpath("/t2/home/.snapshot/")
#indexpath2("/home")
#indexpath2("/home")
#indexpath2("/home/media/Shorts")
#[root@static tests]# more $( python3 -c "import os;os.sys.stdout.buffer.write(b'/home/toppk/crap/phonegames/s40game/Gameloft\xbe\xad\xb5\xe4\xd3\xce\xcf\xb7\xc8\xab\xbc\xaf/XIII/XIII.jad')" )
def main():
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "home":
            indexpath2("/home")
        elif cmd == "needsum":
            missingsum()
        elif cmd == "givesum":
            if len(sys.argv) == 5:
                addsum(sys.argv[2], sys.argv[3], sys.argv[4])
            else:
                print("need volumeid fileid chksum")
        elif cmd == "shorts":
            indexpath2("/home/media/Shorts")
        elif cmd == "index":
            if len(sys.argv) == 3:
                index(sys.argv[2])
            else:
                print("need path")
        elif cmd == "createdb":
            createdb()
        else:
            print("unknown %s" % sys.argv)
    else:
        print("yoyo %s" % sys.argv)
if __name__ == "__main__":
    main()
