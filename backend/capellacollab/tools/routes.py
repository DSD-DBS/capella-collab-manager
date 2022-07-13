import typing as t

from fastapi import APIRouter, Depends
from requests import Session
from capellacollab.core.authentication.jwt_bearer import JWTBearer

from capellacollab.core.database import get_db

from . import crud


router = APIRouter()


@router.get('/')
def get_tools(db: Session = Depends(get_db), token = Depends(JWTBearer())):
    return crud.get_all_tools(db)

@router.get('/versions')
def get_tool_versions(db: Session = Depends(get_db), token = Depends(JWTBearer())):
    return crud.get_versions(db)

@router.get('/types')
def get_tool_types(db: Session = Depends(get_db), token = Depends(JWTBearer())):
    return crud.get_types(db)
