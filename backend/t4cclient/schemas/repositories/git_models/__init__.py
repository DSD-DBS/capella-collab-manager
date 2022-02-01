import typing as t

from pydantic import BaseModel


class RepositoryGitInnerModel(BaseModel):
    path: str
    entrypoint: str
    revision: str

    class Config:
        orm_mode = True


class RepositoryGitModel(BaseModel):
    name: str
    project_id: int
    model: RepositoryGitInnerModel

    class Config:
        orm_mode = True


class PatchRepositoryGitModel(BaseModel):
    primary: t.Optional[bool]


class GetRepositoryGitModel(RepositoryGitModel):
    id: int
    primary: bool
