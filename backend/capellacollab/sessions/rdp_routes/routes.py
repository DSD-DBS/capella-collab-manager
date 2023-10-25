# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.sessions import injectables as sessions_injectables
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s

from . import exceptions, models

router = fastapi.APIRouter()


@router.post("", response_model=models.SessionRoute)
def post_public_route(
    session: sessions_models.DatabaseSession = fastapi.Depends(
        sessions_injectables.get_existing_session
    ),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
):
    # FIXME: Check if it already exists
    # FIXME: Only allow if global flag is set
    # FIXME: Don't allow for Juypter sessions (only RDP sessions)

    try:
        service = operator._create_service(
            name=session.id + "-public",
            deployment_name=session.id,
            ports={"rdp": 3389},
            public=True,
        )
    except Exception:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "SESSION_ROUTE_ALREADY_AVAILABLE",
                "reason": (
                    "We do not support multiple session routes at the moment. "
                    "Please use the existing route."
                ),
            },
        )

    return models.SessionRoute(
        host=None,
        username="techuser",
        password=session.rdp_password,
    )


@router.get("", response_model=models.SessionRoute)
def get_public_route(
    session: sessions_models.DatabaseSession = fastapi.Depends(
        sessions_injectables.get_existing_session
    ),
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
):
    # FIXME: Check if it already exists
    # FIXME: Only allow if global flag is set
    # FIXME: Don't allow for Juypter sessions (only RDP sessions)
    service = (
        operator.get_external_hostname_or_ip_from_service(session.id)
        + ":"
        + operator.get_node_port_from_service(session.id)
    )

    return models.SessionRoute(
        host=operator.get_external_ip_from_service(),
        username="techuser",
        password=session.rdp_password,
    )
