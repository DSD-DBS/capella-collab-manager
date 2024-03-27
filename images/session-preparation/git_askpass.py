#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import sys

if __name__ == "__main__":
    print(os.environ["GIT_" + sys.argv[1].split()[0].upper()])
    raise SystemExit(0)
