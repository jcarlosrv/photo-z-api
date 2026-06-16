import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID = {"u": 19.5, "g": 18.2, "r": 17.5, "i": 17.1, "z": 16.9}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_model_info_features(client):
    resp = client.get("/model/info")
    assert resp.status_code == 200
    assert resp.json()["features"] == [
        "u", "g", "r", "i", "z", "u_g", "g_r", "r_i", "i_z"
    ]


def test_predict_happy_path(client):
    resp = client.post("/predict", json=VALID)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["redshift"], (int, float))
    assert body["magnitude_range"] in {"in", "below", "above"}


def test_predict_above_range(client):
    payload = {"u": 25.0, "g": 24.2, "r": 23.6, "i": 23.1, "z": 22.8}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    assert resp.json()["magnitude_range"] == "above"


def test_predict_missing_field(client):
    payload = {"u": 19.5, "g": 18.2, "r": 17.5, "i": 17.1}
    assert client.post("/predict", json=payload).status_code == 422


def test_predict_out_of_bounds(client):
    payload = {**VALID, "r": 999}
    assert client.post("/predict", json=payload).status_code == 422


def test_predict_extra_field(client):
    payload = {**VALID, "foo": 1}
    assert client.post("/predict", json=payload).status_code == 422


def test_predict_batch(client):
    payload = {"items": [VALID, {"u": 20.1, "g": 19.0, "r": 18.4, "i": 18.0, "z": 17.7}]}
    resp = client.post("/predict/batch", json=payload)
    assert resp.status_code == 200
    assert len(resp.json()["predictions"]) == 2