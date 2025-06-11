# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi

router = fastapi.APIRouter()


@router.get(
    "",
    tags=["Pipelines"],
)
def get_pipelines_overview(
    # db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    pass
    # scheduling.scheduler.get_jobs()
