from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "YOUR_SECRET_KEY_YOUR_SECRET_KEY_YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    principal_id: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_user_db = {
    "alice": {
        "principal_id": "alice-1",
        "username": "alice",
        "hashed_password": "$2b$12$vbl8rX6us6.6Pbow2QYMleyzryMJC2PNOIH/QRdVZd2sBSakKXqyO",  # "secret" hashed
    },
    "bob": {
        "principal_id": "bob-1",
        "username": "bob",
        "hashed_password": "$2b$12$vbl8rX6us6.6Pbow2QYMleyzryMJC2PNOIH/QRdVZd2sBSakKXqyO",  # "secret" hashed
    }
}

def authenticate_user(username: str, password: str):
    """ Check username + password against fake_user_db. """
    user = fake_user_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Create JWT from data + expiration. """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """ 
    Dependency that reads the token from 'Authorization: Bearer <token>',
    validates it, and returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_dict = fake_user_db.get(token_data.username)
    if user_dict is None:
        raise credentials_exception
    return User(username=user_dict["username"], principal_id=user_dict["principal_id"])