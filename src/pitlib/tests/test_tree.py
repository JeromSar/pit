# Disable silly DeprecationErrors from fs.memoryfs
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from fs.memoryfs import MemoryFS
import pytest
from pitlib import db
from pitlib.tree import Tree

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

def test_empty_tree():
    t = Tree.from_fs(FS)