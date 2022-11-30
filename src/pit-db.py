import subprocess
import sys
import hashlib
from pathlib import Path

import argh

HASH_LEN = 64 # hex chars, sha256

def objpath():
    proj_path = Path.cwd().joinpath("test")
    pit_path = proj_path.joinpath(".pit")
    objects_path = pit_path.joinpath("objects")
    
    assert pit_path.exists(), "Expect {} to exist".format(pit_path)
    assert pit_path.is_dir(), "Expect {} to be a directory".format(pit_path)
    
    if not objects_path.exists():
        objects_path.mkdir()
    assert objects_path.is_dir(), "Expect {} to be a directory".format(objects_path)
    return objects_path


def dig2path(digest, exists):
    objects_path = objpath()
    
    digest = digest.strip().lower()
    assert len(digest) > 0, "Expect digest to be greater than 0 length"
    assert len(digest) <= HASH_LEN, "Expect digest to be maximally {} characters long".format(HASH_LEN)

    if len(digest) == HASH_LEN:
        thisobj_path = objects_path.joinpath(digest[0:2], digest[2:])
        assert not thisobj_path.is_dir(), "Expect {} to not be a directory".format()
        if exists: assert thisobj_path.is_file(), "Expect {} to be a file".format(thisobj_path)
        return thisobj_path
    assert exists, "Incomplete object: {}".format(digest)
    
    # Break digest into two pieces. 0:2 and 2:0.
    # Be smart about edge cases like 1 and 2 characters where rest_match == ""
    subfolder_match = digest[0:min(2,len(digest))]
    rest_match = "" if len(digest) <= 2 else digest[2:]
    
    match_object_dirs = list(filter(lambda d: d.name.startswith(subfolder_match), objects_path.iterdir()))
    if len(match_object_dirs) == 0:
        print("No object found starting with:", digest, "(subfolder)")
        exit(1)
    if len(match_object_dirs) != 1:
        print("Found multiple objects matching:", digest, "(subfolder)")
        exit(1)
    object_subdir = match_object_dirs[0]
        
    objects = list(filter(lambda d: d.name.startswith(rest_match), object_subdir.iterdir()))
    if len(objects) == 0:
        print("No object found starting with:", digest, "(in subfolder)")
        exit(1)
    if len(objects) != 1:
        print("Found multiple objects matching:", digest, "(in subfolder)")
        exit(1)
    return objects[0]

def put():
    bytes_in = b''
    hash = hashlib.sha256()
    while True:
        br = sys.stdin.buffer.read(1024)
        if br == b'':
            break
        bytes_in += br
        hash.update(br)
    # print("putting: '{}'".format(bytes_in))
    digest = hash.hexdigest()
    # print("digest: '{}'".format(dig))

    thisobj_path = dig2path(digest, exists=False)
    
    if not thisobj_path.parent.exists():
        thisobj_path.parent.mkdir()
    assert thisobj_path.parent.is_dir(), "Expect {} to be a directory".format(thisobj_path)
    thisobj_path.write_bytes(bytes_in)
    print(digest)
    
def get():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    
    obj_path = dig2path(digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    
    with open(obj_path, "rb") as f:
        while True:
            bytes_read = f.read(1024)
            if bytes_read == b'':
                break
            sys.stdout.buffer.write(bytes_read)

def delete():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    
    # Delete
    obj_path = dig2path(digest, exists=True)
    assert obj_path.is_file(), "Expect {} to be a file".format(obj_path)
    obj_path.unlink()
    
    # Delete parent subdir
    parent_empty = not any(obj_path.parent.iterdir())
    if parent_empty: obj_path.parent.rmdir()

def gethash():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    object_path = dig2path(digest, exists=True)
    print(object_path.parent.name + object_path.name)

def main():
    parser = argh.ArghParser()
    # TODO: Better passthrough without -- 
    parser.add_commands([
        put,
        get,
        delete,
        gethash,
    ])
    parser.dispatch()

if __name__ == '__main__':
    main()
    
