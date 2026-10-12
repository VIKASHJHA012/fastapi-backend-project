from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt,JWTError
from schemas import UserRegister,UserResponse,UserLogin,TokenResponse
from datetime import timezone, timedelta, datetime
from models import User
from Utilities.security import hash_password,verify_password,create_token
from database import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from config import SECRET_KEY

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=201,summary = "Register a new user",    description = "Creates a new user account",
             responses={
                 409:{"description":"Email is already registered"}
             })
async def register_user(user : UserRegister,db = Depends(get_db)):
    # x = 1/0
    # existing_user = db.query(User).filter(User.email == user.email).first()

    statement = (
        select(User)
        .options(selectinload(User.posts))
        .filter(User.email == user.email)
    )

    result = await db.execute(statement)
    existing_user = result.scalars().first()

    if existing_user is not None:
        raise HTTPException(status_code=409,detail='Email is already registered. Please use a different Email to Register or login using existing password.')

    hashed_password = hash_password(user.password)
    

    registration_detail = User(
        name = user.name,
        email = user.email,
        password = hashed_password.decode()
    )
    db.add(registration_detail)
    await db.commit()
    await db.refresh(registration_detail,attribute_names =['posts'])

    return registration_detail

# expire = datetime.now(timezone.utc) + timedelta(minutes=2)
@router.post("/login",responses={401:{"description":"Invalid credentials"}},response_model=TokenResponse)
async def login_user(user:UserLogin,db = Depends(get_db)):

    # existing_user = db.query(User).filter(User.email==user.email).first()
    statement = (
        select(User)
        .filter(User.email == user.email)
    )
    result = await db.execute(statement)
    existing_user = result.scalars().first()
    #checking if user is present or not
    if existing_user is None:
        raise HTTPException(status_code=401,detail="Invalid Credential")
     
    #comparing user's password with the password of user to generate the token
    if verify_password(user.password,existing_user.password):
        access_token = create_token(existing_user,"access")
        refresh_token = create_token(existing_user,"refresh")
        
        # return{
        #     "access token":access_token,
        #     "refresh token":refresh_token,
        #     "token type":"bearer"
        # }
        return TokenResponse(
            access_token= access_token,
            refresh_token= refresh_token,
            token_type = "bearer"
        )
    else:
        raise HTTPException(status_code=401,detail="Invalid Credential")

security = HTTPBearer()

async def _verify_token(
    my_token: HTTPAuthorizationCredentials,
    db,
    expected_type: str
):
    try:
        payload = jwt.decode(
            my_token.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload["type"] != expected_type:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )

        email = payload["email"]

        # user_details = (
        #     db.query(User)
        #     .filter(User.email == email)
        #     .first()
        # )
        statement = (
            select(User)
            .filter(User.email == email)

        )
        result = await db.execute(statement)

        user_details  = result.scalars().first()

        if user_details is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )

        return user_details

    except JWTError:
        logger.warning("JWT Verification failed")
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

async def get_current_user(
    my_token: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    return await _verify_token(my_token,db,expected_type="access"
    )

async def get_current_users_refresh_token(
    my_token: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    return await _verify_token(
        my_token,
        db,
        expected_type="refresh"
    )



    

    


    
