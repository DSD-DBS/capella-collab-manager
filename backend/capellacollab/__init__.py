# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from importlib import metadata

try:
    __version__ = metadata.version("capellacollab-backend")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
del metadata
