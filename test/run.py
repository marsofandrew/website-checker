#!/usr/bin/python
import os
import sys
from pathlib import Path


if __name__ == '__main__':
    path = Path(__file__).parent.parent.absolute()
    sys.path.append(str(path) + "/src/")
    sys.path.append(str(path) + "/src/common")

    os.system("python -m unittest discover -p tests")