# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from . import models


def get_dockerimages_by_environment(
    db: Session, environment: str
) -> models.DB_Dockerimages:
    return (
        db.query(models.DB_Dockerimages)
        .filter(models.DB_Dockerimages.environment == environment)
        .first()
    )


def update_dockerimages_for_environment(
    db: Session, environment: str, config: models.Dockerimages
) -> models.DB_Dockerimages:
    dockerimages = get_dockerimages_by_environment(db, environment)
    dockerimages.persistentworkspace = config.workspaces.persistent
    dockerimages.readonlyworkspace = config.workspaces.readonly
    db.commit()
    return dockerimages
