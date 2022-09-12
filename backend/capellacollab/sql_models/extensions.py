# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging
from importlib import metadata

log = logging.getLogger(__name__)

# Load extension models
eps = (
    metadata.entry_points()["capellacollab.extensions.backups"]
    + metadata.entry_points()["capellacollab.extensions.modelsources"]
)
for ep in eps:
    log.info("Import models of extension %s", ep.name)
    importlib.import_module(".models", ep.module)
