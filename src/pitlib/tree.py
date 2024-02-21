import fs

import pitlib.db as db

from attrs import define, field

@define
class TreeEntry():
    # TODO: better typing?
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

    @staticmethod
    def from_text(text):
        entries = []
        for line in text.splitlines():
            line = line.strip()
            parts = line.split("\t")
            entries.append(TreeEntry(parts[0], parts[1], parts[2]))
        return Tree(entries)


    @staticmethod
    def from_fs(dir: fs.base.FS):
        entries = []
        
        dir.makedir("dir1")
        dir.makedirs("dir2/dir3/dir4")
        dir.makedirs("dir2/dir5/dir6/dir7")


        iterator_tuple_to_paths = lambda path_dirs_files: path_dirs_files[0]
        paths = list(sorted(map(iterator_tuple_to_paths, dir.walk())))
        assert False, paths

        for item in paths:
            if item.name.startswith("."):
                continue # TODO: proper .pitignore file
            
            if item.is_dir():
                entries.append(Tree.from_fs(item)) # TODO: avoid recursion
                continue

            entries.append(TreeEntry(
                type="blob",
                hash=db.hash(item.read_bytes()),
                name=item.name
            ))    
        return Tree(entries)
