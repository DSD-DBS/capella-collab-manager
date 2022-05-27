# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 1st party:
# These import statements of the models are required and should not be removed! (SQLAlchemy will not load the models otherwise)
import capellacollab.projects.models
from capellacollab.sql_models import notices, sessions, users
from capellacollab.config import models
