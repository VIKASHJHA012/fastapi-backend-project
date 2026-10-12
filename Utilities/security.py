import bcrypt
from datetime import timedelta,timezone,datetime
from jose import jwt
from config import SECRET_KEY
# from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

def hash_password(password : str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"),salt)

def verify_password(plain_text : str,stored_hash:str):
    is_correct_password=bcrypt.checkpw(plain_text.encode("utf-8"),stored_hash.encode())
    if is_correct_password:
        logger.info("Password verification succeeded")
    else:
        logger.warning("Password verification failed")
    return is_correct_password



def create_token(user,token_type :str)  :
    if token_type =='refresh':
        expire = datetime.now(timezone.utc)+timedelta(minutes=30)
    
    elif token_type =='access':
        expire = datetime.now(timezone.utc)+timedelta(minutes=10)
    else:
        raise ValueError("Invalid Token Type")

    payload = { "id":user.id,
                "name":user.name,
                "email":user.email,
                "exp":expire,
                "type":token_type,
                }
        
    token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
    return token


