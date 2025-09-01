from .main import app

client = TestClient(app)


def test_hash_verify():
    original_data = "This is some data to be hashed."

    # Test hashing
    response = client.post("/hash", json={"data": original_data})
    assert response.status_code == 200
    hash_data = response.json()["hash"]

    # Test successful verification
    response = client.post("/verify", json={"data": original_data, "hash": hash_data})
    assert response.status_code == 200
    assert response.json()["is_valid"] == True

    # Test failed verification
    response = client.post("/verify", json={"data": "wrong data", "hash": hash_data})
    assert response.status_code == 200
    assert response.json()["is_valid"] == False
