import typing as t

import t4cclient.extensions.t4c as t4c_manager
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from t4cclient.core.database import get_db
from t4cclient.core.oauth.jwt_bearer import JWTBearer
from t4cclient.routes.open_api_configuration import AUTHENTICATION_RESPONSES
from t4cclient.schemas.sessions import GetSessionUsageResponse

router = APIRouter()


@router.get(
    "/",
    response_model=GetSessionUsageResponse,
    responses=AUTHENTICATION_RESPONSES,
    dependencies=[Depends(JWTBearer())],
)
def get_session_usage():
    return t4c_manager.get_t4c_status()
