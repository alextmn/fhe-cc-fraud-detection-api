def test_fhe_encrypt(shared_token):
    
    from fhe_data_import import import_csv_to_mongo
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

def test_fhe_e2e_all(shared_token):
    response = client.post("/fhe_generate_keypair", 
                             headers={"Authorization": f"Bearer {shared_token}"},
                           json={"name": 'e2e-test'})
    assert response.status_code == 200

    response = client.get("/keypairs",
                           headers={"Authorization": f"Bearer {shared_token}"})

    assert len(response.json()) > 0 
    key_id = response.json()[0]["key_id"]

    response = client.post("/transactions",
                           headers={"Authorization": f"Bearer {shared_token}"},)

                            
    assert response.status_code == 200
    tx = response.json()[0]
    vec = tx['v_vector']
    print(vec)

    response = client.post("/fhe_encrypt",
                           headers={"Authorization": f"Bearer {shared_token}"},
                            json={"v": vec, "key_id": key_id})
                           
    assert response.status_code == 200
