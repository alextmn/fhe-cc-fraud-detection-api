import pytest
from fastapi.testclient import TestClient
from fhe_app import app, dao
from typing import List

client = TestClient(app)

def test_fhe_generate_keypair():
    name = "test_keypair"
    response = client.post("/fhe_generate_keypair", json={"name": name})
    assert response.status_code == 200
    data = response.json()
    
    assert "key_id" in data
    assert data["name"] == name
    assert "created" in data
    assert "expired" in data

def test_get_keypairs():

    response = client.get("/keypairs")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0  

def test_fhe_encrypt():
    response = client.post("/fhe_encrypt")
    assert response.status_code == 200
    

    