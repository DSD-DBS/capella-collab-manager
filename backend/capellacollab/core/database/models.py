# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=unused-import
# These import statements of the models are required and should not be removed! (SQLAlchemy will not load the models otherwise)

import capellacollab.notices.models
import capellacollab.projects.models
import capellacollab.projects.toolmodels.backups.models
import capellacollab.projects.toolmodels.backups.runs.models
import capellacollab.projects.toolmodels.models
import capellacollab.projects.toolmodels.modelsources.git.models
import capellacollab.projects.toolmodels.modelsources.t4c.models
import capellacollab.projects.toolmodels.restrictions.models
import capellacollab.projects.users.models
import capellacollab.sessions.models
import capellacollab.settings.integrations.purevariants.models
import capellacollab.settings.modelsources.git.models
import capellacollab.settings.modelsources.t4c.models
import capellacollab.tools.integrations.models
import capellacollab.tools.models
import capellacollab.users.events.models
import capellacollab.users.models
import capellacollab.users.tokens
