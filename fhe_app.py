from fhe_auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, User, authenticate_user, create_access_token, get_current_user
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from fhe_dao import DAO
from datetime import datetime, timedelta
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



app = FastAPI()
dao = DAO()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class KeyPairResponse(BaseModel):
    key_id: str
    name: str
    created: datetime
    expired: datetime



class KeyPairRequest(BaseModel):
    name: str

class EncryptRequest(BaseModel):
    key_id: str
    v: List[float]

@app.get("/health")
@app.get("/")
def fhe_health():
    return {"health": "healthy"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create the token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/fhe_generate_keypair", response_model=KeyPairResponse)
def fhe_generate_keypair(data: KeyPairRequest, current_user: User = Depends(get_current_user)):
    created = datetime.utcnow()
    expired = created + timedelta(days=256)
    name = data.name
    
    key_pair = dao.generate_keypair(name,
                                     current_user.principal_id, 
                                     created, expired)
    return KeyPairResponse(
        key_id=key_pair.key_id,
        name=name,
        created=created,
        expired=expired
    )

@app.get("/keypairs", response_model=List[KeyPairResponse])
def get_keypairs(current_user: User = Depends(get_current_user)):
    key_pairs = dao.get_all_keypairs(current_user.principal_id)
    return [
        KeyPairResponse(
            key_id=key_pair.key_id,
            name=key_pair.name,
            created=key_pair.created,
            expired=key_pair.expired
        )
        for key_pair in key_pairs
    ]

@app.delete("/fhe_remove_keypair/{key_id}")
def fhe_remove_keypair(key_id: str, current_user: User = Depends(get_current_user)):
    if not dao.remove_keypair(key_id):
        raise HTTPException(status_code=404, detail="KeyPair not found")
    return {"message": "KeyPair deleted successfully"}

@app.post("/transactions")
def fhe_cc_transactions(current_user: User = Depends(get_current_user)):
    t_list = dao.get_cc_transactions(current_user.principal_id)
    return t_list

@app.get("/protected-route")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username} -  {current_user.principal_id}. You are authorized!"}

@app.post("/fhe_encrypt")
def fhe_encrypt(data:EncryptRequest, current_user: User = Depends(get_current_user)):
    #key_pair = dao.pub_key(current_user.principal_id)[0]
    dao.fhe_encrypt_db(data.key_id, current_user.principal_id, data.v)
    print(data.key_id)
    return {}