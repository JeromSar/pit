import sys
from pathlib import Path

import argh

import pitlib.db as db

def put():
    bytes_in = b''
    while True:
        br = sys.stdin.buffer.read(1024)
        if br == b'':
            break
        bytes_in += br
    print(db.put(bytes_in))
    
def get():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    sys.stdout.buffer.write(db.get(digest))

def delete():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    db.delete(digest)
    

def gethash():
    data = sys.stdin.readlines()
    assert len(data) == 1, "Expect one line of input"
    digest = data[0].strip()
    print(db.gethash(digest))

def main():
    parser = argh.ArghParser()
    parser.add_commands([
        put,
        get,
        delete,
        gethash,
    ])
    parser.dispatch()

if __name__ == '__main__':
    main()
    
