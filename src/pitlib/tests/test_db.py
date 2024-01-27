
# Disable silly DeprecationErrors from fs.memoryfs
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from pathlib import Path
import sys
from fs.memoryfs import MemoryFS
import pytest

# Make sure we can import the main Python source files
# SRC_PATH = Path(__file__).parents[1].joinpath("src")
# assert SRC_PATH.exists()
# sys.path.insert(0, str(SRC_PATH))

from pitlib import db

# Virtual filesystem used for testing
FS = None

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup in-memory virtual filesystem for tests
    global FS
    FS = MemoryFS()
    db.FS = FS
    yield # run the test
    FS.close()
    FS = None
    db.FS = None
    
#
# db.hash
#

def test_hash_empty():
    assert db.hash(b"") == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    assert db.hash("") == "da39a3ee5e6b4b0d3255bfef95601890afd80709"

def test_hash_hello():
    # e.g., http://www.sha1-online.com/
    assert db.hash(b"hello") == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
    assert db.hash("hello") == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

def test_hash_none():
    with pytest.raises(ValueError):
        db.hash(None)
    with pytest.raises(ValueError):
        db.hash(False)
    with pytest.raises(ValueError):
        db.hash(True)

#
# db.db_path
#

def test_db_path():
    path = db.db_path(expect_exists=False)
    assert path is not None
    assert path != ""

def test_db_path_notexists():
    with pytest.raises(Exception):
        db.db_path(expect_exists=True)
    assert not FS.exists(db.db_path(expect_exists=False))

def test_db_path_init():
    db.init_db()
    assert FS.isdir(db.db_path(expect_exists=True))

def test_db_path_same():
    assert db.db_path(expect_exists=False) == db.db_path(expect_exists=False)

#
# db.init
#

def test_init():
    path = db.db_path(expect_exists=False)
    assert not FS.exists(path)
    db.init_db()
    assert FS.exists(path)

def test_doubleinit():
    path = db.db_path(expect_exists=False)
    assert not FS.exists(path)
    db.init_db()
    db.init_db()
    assert FS.exists(path)

def test_init_db_file():
    path = db.db_path(expect_exists=False)
    assert not FS.exists(path)
    FS.create(path)
    with pytest.raises(Exception):
        db.init_db()

def test_init_pit_same():
    db.init_db()
    assert db.db_path() == db.db_path()

def test_init_pit_same2():
    assert db.db_path(expect_exists=False) == db.db_path(expect_exists=False)

def test_init_pit_same3():
    path = db.db_path(expect_exists=False) 
    db.init_db()
    path2 = db.db_path(expect_exists=False)
    assert path == path2
    assert path == db.db_path()

#
# objs_path
#

def test_objs_noinit():
    with pytest.raises(Exception):
        db.objs_path()

def test_objs_dir():
    db.init_db()
    assert FS.isdir(db.objs_path())

def test_objs_init():
    db.init_db()
    db.objs_path()
    assert FS.exists(db.objs_path())
    assert FS.isdir(db.objs_path())

def test_objs_file():
    db.init_db()
    path = db.objs_path()
    FS.removedir(path)
    FS.create(path)
    with pytest.raises(Exception):
        db.objs_path()

def test_objs_in_db():
    db.init_db()
    assert db.objs_path().startswith(db.db_path())

#
# db.refs_path
#
def test_refs_noinit():
    with pytest.raises(Exception):
        db.refs_path()

def test_refs_dir():
    db.init_db()
    assert FS.isdir(db.refs_path())

def test_refs_init():
    db.init_db()
    db.refs_path()
    assert FS.exists(db.refs_path())
    assert FS.isdir(db.refs_path())

def test_refs_file():
    db.init_db()
    path = db.refs_path()
    FS.removedir(path)
    FS.create(path)
    with pytest.raises(Exception):
        db.refs_path()

def test_refs_in_db():
    db.init_db()
    assert db.objs_path().startswith(db.db_path())

#
# db.digest_to_path
#

def test_d2p_invalid():
    db.init_db()
    with pytest.raises(ValueError):
        db.digest_to_path(None)
    with pytest.raises(ValueError):
        db.digest_to_path("")
    with pytest.raises(ValueError):
        db.digest_to_path(True)
    with pytest.raises(ValueError):
        db.digest_to_path("hello")
    with pytest.raises(ValueError):
        db.digest_to_path(b"hello")

def test_d2p_simple():
    db.init_db()
    digest = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    path = db.digest_to_path(digest)
    assert path.startswith(db.objs_path())
    assert path != db.objs_path()
    assert path != db.objs_path() + '/' + digest
    assert '/' in path
    assert not FS.exists(path)

def test_d2p_different():
    db.init_db()
    digest1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    digest2 = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
    assert db.digest_to_path(digest1) != db.digest_to_path(digest2)

def test_d2p_caps():
    db.init_db()
    digest1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    digest2 = "dA39a3ee5e6b4b0d3255bfef95601890afd80709"
    assert db.digest_to_path(digest1) == db.digest_to_path(digest2)

def test_d2p_caps2():
    db.init_db()
    digest1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    digest2 = "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709"
    assert db.digest_to_path(digest1) == db.digest_to_path(digest2)

#
# db.put
#

def test_put_noinit():
    with pytest.raises(Exception):
        db.put("hello")
    with pytest.raises(Exception):
        db.put(b"hello")


@pytest.mark.parametrize("data", [None, False, True, 1, 0, -1])
def test_put_invalid(data):
    db.init_db()
    with pytest.raises(ValueError):
        db.put(data)

@pytest.mark.parametrize("data", ["hello", "Hello", b"hello", "", b"", b"\0\x234234", b"\0\0\xe2\x80\x9d"])
def test_put_simple(data):
    db.init_db()
    assert not FS.exists(db.digest_to_path(db.hash(data)))
    digest = db.put(data)
    assert len(digest) == db.HASH_LEN
    assert digest == db.hash(data)
    path = db.digest_to_path(digest)
    assert FS.exists(path)

    # This may be testing too much of the internal API. Remove if it becomes a problem
    if isinstance(data, str):
        assert FS.readtext(path, encoding='utf-8') == data
    elif isinstance(data, bytes):
        assert FS.readbytes(path) == data
    else:
        assert False

def test_put_count():
    datas = [b"hello", b"", b"\0\x234234", b"\0", b"\0\0\xe2\x80\x9d"]
    db.init_db()
    for data in datas:
        db.put(data)
    files_created = 0
    for path, info in FS.walk.info():
        if not info.is_dir:
            files_created += 1
    assert files_created == len(datas)

#
# db.get
#
def test_put_noinit():
    with pytest.raises(Exception):
        db.get("da39a3ee5e6b4b0d3255bfef95601890afd80709")
    with pytest.raises(Exception):
        db.get(b"da39a3ee5e6b4b0d3255bfef95601890afd80709")

@pytest.mark.parametrize("data", [None, False, True, 1, 0, -1])
def test_get_invalid(data):
    db.init_db()
    with pytest.raises(Exception):
        db.get(data)

@pytest.mark.parametrize("data", [b"hello", b"", b"\0\x234234", b"\0", b"\0\0\xe2\x80\x9d"])
def test_put_get(data):
    db.init_db()
    digest = db.put(data)
    if isinstance(data, str): data = data.encode('utf-8')
    assert db.get(digest) == data

def test_put_get_multi():
    datas = [b"hello", b"", b"\0\x234234", b"\0", b"\0\0\xe2\x80\x9d"]
    digests = []
    db.init_db()
    for data in datas:
        digests.append(db.put(data))
    for (data, digest) in zip(datas, digests):
        assert db.get(digest) == data

