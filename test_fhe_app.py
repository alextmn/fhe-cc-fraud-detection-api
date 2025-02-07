from fhe_data_import import import_csv_to_mongo
import pytest
from fastapi.testclient import TestClient
from fhe_app import app, dao
from typing import List

client = TestClient(app)

@pytest.fixture(scope="session")
def shared_token():
    import_csv_to_mongo()
    response = client.post("/login", data={"username": "alice", "password": "secret"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

def test_fhe_generate_keypair(shared_token):

    name = "test_keypair"
    response = client.post("/fhe_generate_keypair", 
                             headers={"Authorization": f"Bearer {shared_token}"},
                           json={"name": name})
    assert response.status_code == 200
    data = response.json()
    
    assert "key_id" in data
    assert data["name"] == name
    assert "created" in data
    assert "expired" in data

def test_get_keypairs(shared_token):

    response = client.get("/keypairs",
                          headers={"Authorization": f"Bearer {shared_token}"},)
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0  

def test_fhe_encrypt(shared_token):
    response = client.post("/fhe_encrypt",
                           headers={"Authorization": f"Bearer {shared_token}"},)
    assert response.status_code == 200

def test_fhe_transactions(shared_token):
    response = client.post("/transactions",
                           headers={"Authorization": f"Bearer {shared_token}"},)
                           
    assert response.status_code == 200
    print (response.json()[0])
    

    