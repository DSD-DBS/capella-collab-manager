# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import importlib
import logging
from importlib import metadata

# These import statements of the models are required and should not be removed! (SQLAlchemy will not load the models otherwise)
import capellacollab.projects.models
import capellacollab.config.models
import capellacollab.users.models
import capellacollab.sessions.models
import capellacollab.tools.models
from capellacollab.sql_models import extensions, notices

log = logging.getLogger(__name__)

# Load models of modelsources
eps = metadata.entry_points()["capellacollab.settings.modelsources"]
for ep in eps:
    log.info("Import models of extension %s", ep.name)
    try:
        importlib.import_module(".models", ep.module)
    except ModuleNotFoundError:
        log.error("Ignore module %s.models. Module not found.")
