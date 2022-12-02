from pathlib import Path

import pitlib.db as db

from attrs import define, field

@define
class Entry():
    type: str = field()
    hash: str = field()
    name: str = field()
    
    @type.validator
    def check(self, attribute, value):
        assert value == "blob" or value == "tree"
        
    @hash.validator
    def check(self, attribute, value):
        assert len(value) == db.HASH_LEN

    def __init__(self, type, hash, name):
        
        # TODO: add file mode
        self.type = type
        self.hash = hash
        self.name = name

@define
class Tree():
    entries: list = field(factory=list)

    def to_text(self):
        s = ""
        for entry in self.entries:
            s += f"{entry.type}\t{entry.hash}\t{entry.name}\n"
        return s

def from_text(text):
    entries = []
    for line in text.splitlines():
        line = line.strip()
        parts = line.split("\t")
        entries.append(Entry(parts[0], parts[1], parts[2]))
    return Tree(entries)


def from_dir(dir: Path):
    assert dir.is_dir()
    entries = []
    
    contents = list(sorted(dir.iterdir()))
    for item in contents:
        if item.name.startswith("."):
            continue # TODO: proper .pitignore file
        
        if item.is_dir():
            entries.append(from_dir(item))
            continue

        entries.append(Entry(
            type="blob",
            hash=db.hash(item.read_bytes()),
            name=item.name
        ))    
    return Tree(entries)
