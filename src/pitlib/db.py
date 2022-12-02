
import hashlib
from pathlib import Path

HASH_LEN = 40 # hex chars, sha1

def objpath():
    # TODO: Recursively find the parent
    proj_path = Path.cwd()
    pit_path = proj_path.joinpath(".pit")
    objects_path = pit_path.joinpath("objects")
    
    assert pit_path.exists(), "Expect {} to exist".format(pit_path)
    assert pit_path.is_dir(), "Expect {} to be a directory".format(pit_path)
    
    if not objects_path.exists():
        objects_path.mkdir()
    assert objects_path.is_dir(), "Expect {} to be a directory".format(objects_path)
    return objects_path


def dig2path(partial_digest, exists):
    objects_path = objpath()
    
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

def put(bytes_in):
    hash = hashlib.sha1()
    hash.update(bytes_in)
    digest = hash.hexdigest()
    thisobj_path = dig2path(digest, exists=False)
    
    if not thisobj_path.parent.exists():
        thisobj_path.parent.mkdir()
    assert thisobj_path.parent.is_dir(), "Expect {} to be a directory".format(thisobj_path)
    thisobj_path.write_bytes(bytes_in)
    return digest

def get(partial_digest):
    obj_path = dig2path(partial_digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    
    bytes_out = b''
    with open(obj_path, "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if bytes_read == b'':
                break
            bytes_out += bytes_read
    return bytes_out

def delete(partial_digest):
    # Delete
    obj_path = dig2path(partial_digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    obj_path.unlink()
    
    # Delete parent subdir
    parent_empty = not any(obj_path.parent.iterdir())
    if parent_empty: obj_path.parent.rmdir()
    
def gethash(partial_digest):
    object_path = dig2path(partial_digest, exists=True)
    return object_path.parent.name + object_path.name
