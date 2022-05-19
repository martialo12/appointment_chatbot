from fastapi.testclient import TestClient
from app.application import app


client = TestClient(app)


def test_get_all_users():
    response = client.get("/all_users")
    assert response.status_code == 200


def test_get_user_by_email():
    email = "martial.hermann.wafo@pwc.com"
    response = client.get(f"/get_user_by_email/{email}")
    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "external_sub_id": "3e5959d0-4d11-440a-a5b5-7fe6e1e4f603",
            "id": 1,
            "email": "martial.hermann.wafo@pwc.com",
            "created_at": None,
            "internal_sub_id": "$2b$12$906253bb973d1a3611f27u4fnB.uYZjldGc5TkRSK2e3loubE2gh.",
            "username": "Martial Hermann",
            "uid": "mwafo001",
            "role": "ADMIN",
        }
    }


def test_get_all_users_by_role():
    roles = ("admin", "user", "tbudget")
    for role in roles:
        response = client.get(f"/get_all_users_by_role/{role}")
        assert response.status_code == 200

    invalid_role = "pwcuser"
    response = client.get(f"/get_all_users_by_role/{invalid_role}")
    assert response.status_code == 200
    assert response.json() == {"users": []}


def test_get_user_by_internal_sub_id():
    internal_sub_id = "$2b$12$906253bb973d1a3611f27u4fnB.uYZjldGc5TkRSK2e3loubE2gh."
    response = client.get(f"/get_user_by_internal_sub_id/{internal_sub_id}")
    assert response.status_code == 200

    invalid_internal_sub_id = "kd8924092dsd"
    response = client.get(f"/get_user_by_internal_sub_id/{invalid_internal_sub_id}")
    assert response.status_code == 404


def test_create_user():
    data_json = {
        "email": "test@pwc.com",
        "username": "test user",
        "external_sub_id": "test2022",
        "uid": "utest",
        "role": "USER",
    }
    response = client.post("/create_user", json=data_json)
    assert response.status_code == 200


def test_update_role_by_user_id():
    email = "test@pwc.com"
    response = client.get(f"/get_user_by_email/{email}")
    user_id = response.json()["user"]["id"]
    data_json = {"role": "admin"}
    response = client.put(f"/update_role_by_user_id/{user_id}", json=data_json)
    assert response.status_code == 200


def test_update_user_by_user_id():
    email = "test@pwc.com"
    response = client.get(f"/get_user_by_email/{email}")
    user_id = response.json()["user"]["internal_sub_id"]
    data_json = {"username": "new test user", "role": "admin"}
    response = client.put(f"/update_user_by_internal_sub_id/{user_id}", json=data_json)
    assert response.status_code == 200


def test_search_all_users():
    response = client.get("/search_all_users?page=1&per_page=5&role=admin")
    assert response.status_code == 200
    response = client.get("/search_all_users?page=1&per_page=5&id=1")
    assert response.status_code == 200
    response = client.get("/search_all_users?page=1&per_page=5&email=test@pwc.com")
    assert response.status_code == 200
    response = client.get("/search_all_users?page=1&per_page=5&username=martial")
    assert response.status_code == 200
    response = client.get("/search_all_users?page=1&per_page=5&uid=mwafo001")
    assert response.status_code == 200


def test_delete_user_by_email():
    email = "test@pwc.com"
    response = client.delete(f"/delete_user/{email}")
    assert response.status_code == 200
    assert response.json() == {"user": f"{email}", "message": "user deleted"}
