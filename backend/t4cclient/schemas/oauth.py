from pydantic import BaseModel


class TokenRequest(BaseModel):
    code: str
    state: str

class RefreshTokenRequest(BaseModel): 
    refresh_token: str
