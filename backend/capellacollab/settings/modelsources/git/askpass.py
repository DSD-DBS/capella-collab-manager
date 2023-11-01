#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import os
import sys

if __name__ == "__main__":
    print(  # pylint: disable=bad-builtin
        os.environ["GIT_" + sys.argv[1].split()[0].upper()]
    )
    raise SystemExit(0)
