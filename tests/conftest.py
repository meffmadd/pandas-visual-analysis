import sys
import os

if os.path.exists("tests/../src/"):
    sys.path.append("tests/../src/")  # when calling pytest from root

if os.path.exists("../src/"):
    sys.path.append("../src/")  # when calling pytest from tests
