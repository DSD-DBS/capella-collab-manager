from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    USER = "user"
    ADMIN = "administrator"


class PatchUserRoleRequest(BaseModel):
    role: Role


class GetUserResponse(BaseModel):
    id: str
    name: str
    role: Role

    class Config:
        orm_mode = True
