class Entry():
    def __init__(self, type, hash, name):
        assert type == "blob" or type == "tree"
        # TODO: add file mode
        self.type = type
        self.hash = hash
        self.name = name

class Tree():
    def __init__(self, entries=None):
        self.entries = [] if entries == None else entries

    def from_text(text):
        entries = []
        for line in text.splitlines():
            line = line.strip()
            parts = line.split("\t")
            entries.append(Entry(parts[0], parts[1], parts[2]))
        return Tree(entries)

    def to_text(self):
        s = ""
        for entry in self.entries:
            s += f"{entry.type}\t{entry.hash}\t{entry.name}\n"
        return s
