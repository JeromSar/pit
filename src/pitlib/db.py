
import hashlib
from pathlib import Path
from fs.osfs import OSFS

HASH_LEN = 40 # hex chars, sha1

FS = OSFS(".")

def hash(input):
    if input is None or not (isinstance(input, str) or isinstance(input, bytes)):
        raise ValueError("Must provide bytes (parameter is None)")

    if isinstance(input, str):
        input = input.encode(encoding='utf-8')

    hash = hashlib.sha1()
    hash.update(input)
    return hash.hexdigest()

def db_path(expect_exists=True):
    # TODO: Recursively find the parent
    pitfolder = ".pit"
    if expect_exists:
        assert FS.exists(pitfolder), "Expect {} to exist".format(pitfolder)
        assert FS.isdir(pitfolder), "Expect {} to be a directory".format(pitfolder)
    return pitfolder

def init_db():
    pitdir = db_path(expect_exists=False)
    if FS.isdir(pitdir): return
    if FS.exists(pitdir):
        raise AssertionError(".pit is not a directory")
    FS.makedir(pitdir)

def sub_path(dir):
    sub_path = db_path() + f"/{dir}"
    if not FS.exists(sub_path):
        FS.makedir(sub_path)
    assert FS.isdir(sub_path), "Expect {} to be a directory".format(sub_path)
    return sub_path

def objs_path():
    return sub_path("objs")

def refs_path():
    return sub_path("refs")

def digest_to_path(digest):
    if not digest: raise ValueError()
    if not isinstance(digest, str): raise ValueError("Expect digest to be a string")
    if len(digest) != HASH_LEN: raise ValueError(f"Expect digest '{digest}' to be of length {HASH_LEN}")
    digest = digest.lower() # auto-convert paths to lowercase
    return objs_path() + f"/{digest[0]}/{digest[1:]}"

def put(bytes_in):
    digest = hash(bytes_in)
    thisobj_path = digest_to_path(digest)
    
    if not thisobj_path.parent.exists():
        thisobj_path.parent.mkdir()
    assert thisobj_path.parent.is_dir(), "Expect {} to be a directory".format(thisobj_path)
    thisobj_path.write_bytes(bytes_in)
    return digest
    
def get(partial_digest):
    obj_path = partial_digest_to_path(partial_digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    
    bytes_out = b''
    with open(obj_path, "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if bytes_read == b'':
                break
            bytes_out += bytes_read
    return bytes_out

def partial_digest_to_path(partial_digest, exists):
    objects_path = objs_path()
    
    partial_digest = partial_digest.strip().lower()
    assert len(partial_digest) > 0, "Expect digest to be greater than 0 length"
    assert len(partial_digest) <= HASH_LEN, "Expect digest to be maximally {} characters long".format(HASH_LEN)

    if len(partial_digest) == HASH_LEN:
        thisobj_path = objects_path.joinpath(partial_digest[0:2], partial_digest[2:])
        assert not thisobj_path.is_dir(), "Expect {} to not be a directory".format()
        if exists: assert thisobj_path.is_file(), "Expect {} to be a file".format(thisobj_path)
        return thisobj_path
    assert exists, "Incomplete object: {}".format(partial_digest)
    # Break digest into two pieces. 0:2 and 2:0.
    # Be smart about edge cases like 1 and 2 characters where rest_match == ""
    subfolder_match = partial_digest[0:min(2,len(partial_digest))]
    rest_match = "" if len(partial_digest) <= 2 else partial_digest[2:]
    
    match_object_dirs = list(filter(lambda d: d.name.startswith(subfolder_match), objects_path.iterdir()))
    if len(match_object_dirs) == 0:
        print("No object found starting with:", partial_digest, "(subfolder)")
        exit(1)
    if len(match_object_dirs) != 1:
        print("Found multiple objects matching:", partial_digest, "(subfolder)")
        exit(1)
    object_subdir = match_object_dirs[0]
        
    objects = list(filter(lambda d: d.name.startswith(rest_match), object_subdir.iterdir()))
    if len(objects) == 0:
        print("No object found starting with:", partial_digest, "(in subfolder)")
        exit(1)
    if len(objects) != 1:
        print("Found multiple objects matching:", partial_digest, "(in subfolder)")
        exit(1)
    return objects[0]

def resolve_ref(ref, recursive=True):
    refs_path = db_path().joinpath(ref)
    assert refs_path.is_dir(), "Expect {} to be a directory".format(refs_path)
    resolved = None

    if ref.startswith("ref: "):
        ref = ref[5:]
    assert not ref.contains(" "), f"Ref cannot contain space: {ref}"
    
    if ref == "HEAD" or ref.contains("/"):
        # Actual ref: "HEAD" or something like "heads/master"
        ref_path = refs_path.joinpath(*ref.split("/"))
        assert ref_path.is_file(), "Expect {} to be a file".format(ref_path)   
        resolved = ref_path.read_text().strip()

        # Recurse if needed
        if recursive and resolved.startswith("ref: "):
            return resolve_ref(resolved)
        return resolved
    else:
        # Object
        return partial_digest_to_path(partial_digest=ref, exists=True)



def delete(partial_digest):
    # Delete
    obj_path = partial_digest_to_path(partial_digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    obj_path.unlink()
    
    # Delete parent subdir
    parent_empty = not any(obj_path.parent.iterdir())
    if parent_empty: obj_path.parent.rmdir()
    
def gethash(partial_digest):
    object_path = partial_digest_to_path(partial_digest, exists=True)
    return object_path.parent.name + object_path.name

def putref(type, name, hash):
    assert len(hash) == HASH_LEN
    assert type == "heads"
    # TODO: add support for remotes and tags
    refs = refs_path()

    refs_type_path = refs.joinpath(type)
    if not refs_type_path.exists():
        refs_type_path.mkdir()
    assert refs_type_path.is_dir(), "Expect {} to be a directory".format(refs_type_path)
    
    refs_type_path.joinpath(name).write_text(hash)

def getref(type, name):
    assert type == "heads"
    # TODO: add support for remotes and tags
    refs = refs_path()
    refs_type_path = refs.joinpath(type)
    assert refs_type_path.is_dir(), "Expect {} to be a directory".format(refs_type_path)
    ref = refs_type_path.joinpath(name)
    assert ref.is_file(), "Expect {} to be a file".format(ref)
    
    hash = ref.read_text().strip()
    assert len(hash) == HASH_LEN
    return hash

