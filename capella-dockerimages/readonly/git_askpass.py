#!/usr/bin/env python

import os
import sys

if __name__ == "__main__":
    print(os.environ["GIT_" + sys.argv[1].split()[0].upper()])
    raise SystemExit(0)
