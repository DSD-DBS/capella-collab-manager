# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: F401
# These import statements of the models are required and should not be removed! (SQLAlchemy will not load the models otherwise)

import capellacollab.announcements.models
import capellacollab.configuration.models
import capellacollab.events.models
import capellacollab.feedback.models
import capellacollab.projects.models
import capellacollab.projects.permissions.models
import capellacollab.projects.toolmodels.backups.models
import capellacollab.projects.toolmodels.backups.runs.models
import capellacollab.projects.toolmodels.models
import capellacollab.projects.toolmodels.modelsources.git.models
import capellacollab.projects.toolmodels.modelsources.t4c.models
import capellacollab.projects.toolmodels.provisioning.models
import capellacollab.projects.toolmodels.restrictions.models
import capellacollab.projects.tools.models
import capellacollab.projects.users.models
import capellacollab.projects.volumes.models
import capellacollab.sessions.models
import capellacollab.settings.integrations.purevariants.models
import capellacollab.settings.modelsources.git.models
import capellacollab.settings.modelsources.t4c.instance.models
import capellacollab.settings.modelsources.t4c.license_server.models
import capellacollab.tools.models
import capellacollab.users.models
import capellacollab.users.tokens.models
import capellacollab.users.workspaces.models
