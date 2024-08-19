from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email:str
    role_id:int
    


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class GoogleUser(BaseModel):
    sub: int
    email: str
    name: str
    picture: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
    