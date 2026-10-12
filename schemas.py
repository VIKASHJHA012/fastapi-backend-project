from pydantic import BaseModel

class PostResponse(BaseModel):
    id : int
    title : str
    user_id : int

class UserCreate(BaseModel):
    name :str
    email :str 
    
class UserRegister(BaseModel):
    name :str
    email :str 
    password :str

class UserLogin(BaseModel):
    email : str
    password : str

class UserUpdate(BaseModel):
    name :str
    email: str

class UserResponse(BaseModel):
    id : int
    name: str
    email : str
    posts: list[PostResponse]

class UserUpdatePatch(BaseModel):
    name :str | None = None
    email : str | None = None

class PostCreate(BaseModel):
    title: str

class PostUpdatePatch(BaseModel):
    title : str | None = None


class TagCreate(BaseModel):
    title :str

class TagResponse(BaseModel):
    id : int
    tag_name: str

class TokenResponse(BaseModel):
    access_token :str
    refresh_token :str
    token_type : str