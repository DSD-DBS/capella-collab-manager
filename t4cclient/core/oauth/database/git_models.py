import t4cclient.core.database.repository_git_models as crud_git_models
from fastapi import Depends, HTTPException
from t4cclient.core.database import get_db


def verify_gitmodel_permission(repository: str, git_model_id: int, db):
    if (
        crud_git_models.get_model_by_id(db, repository, git_model_id).repository_name
        != repository
    ):
        raise HTTPException(
            status_code=403,
            detail="The Git Model is not part of the specified repository!",
        )
