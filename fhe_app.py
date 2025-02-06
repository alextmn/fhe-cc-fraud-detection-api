from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fhe_dao import DAO
from datetime import datetime, timedelta
from typing import List

app = FastAPI()
dao = DAO()

class KeyPairResponse(BaseModel):
    key_id: str
    name: str
    created: datetime
    expired: datetime

class KeyPairRequest(BaseModel):
    name: str

@app.get("/health")
@app.get("/")
def fhe_health():
    return {"health": "healthy"}

@app.post("/fhe_generate_keypair", response_model=KeyPairResponse)
def fhe_generate_keypair(data: KeyPairRequest):
    created = datetime.utcnow()
    expired = created + timedelta(days=256)
    name = data.name

    key_pair = dao.generate_keypair(name, created, expired)
    return KeyPairResponse(
        key_id=key_pair.key_id,
        name=name,
        created=created,
        expired=expired
    )

@app.get("/keypairs", response_model=List[KeyPairResponse])
def get_keypairs():
    key_pairs = dao.get_all_keypairs()
    return [
        KeyPairResponse(
            key_id=key_pair.key_id,
            name=key_pair.name,
            created=key_pair.created,
            expired=key_pair.expired
        )
        for key_pair in key_pairs
    ]

@app.post("/fhe_keypair", response_model=KeyPairResponse)
def fhe_generate_keypair():
    key_pair = dao.generate_keypair()
    return KeyPairResponse(key_id=key_pair.key_id)

@app.delete("/fhe_remove_keypair/{key_id}")
def fhe_remove_keypair(key_id: str):
    if not dao.remove_keypair(key_id):
        raise HTTPException(status_code=404, detail="KeyPair not found")
    return {"message": "KeyPair deleted successfully"}

@app.post("/fhe_encrypt")
def fhe_generate_keypair():
    key_pair = dao.get_all_keypairs()[0]
    dao.fhe_encrypt_db(key_pair.key_id, [1,2,3,4])
    return {}

