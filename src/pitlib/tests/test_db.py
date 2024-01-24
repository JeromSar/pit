
# Disable silly DeprecationErrors from fs.memoryfs
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from pathlib import Path
import sys
from fs.memoryfs import MemoryFS

# Make sure we can import the main Python source files
# SRC_PATH = Path(__file__).parents[1].joinpath("src")
# assert SRC_PATH.exists()
# sys.path.insert(0, str(SRC_PATH))

from pitlib import db

# Set these tests to be a virtual FS
db.FS = MemoryFS()

def test_db():
    print("Test complete")
