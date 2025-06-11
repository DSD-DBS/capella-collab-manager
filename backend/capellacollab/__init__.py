# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from importlib import metadata as importlib_metadata

try:
    __version__ = importlib_metadata.version("capellacollab-backend")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"
del importlib_metadata
