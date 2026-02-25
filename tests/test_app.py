import copy

import pytest
from fastapi.testclient import TestClient

from src import app
from src.app import activities


@pytest.fixture(autouse=True)
def reset_activities():
    # make a clean deep copy of the original state for each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture

def client():
    return TestClient(app.app)


def test_get_activities_returns_all(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert resp.json() == activities


def test_signup_adds_participant(client):
    activity = "Chess Club"
    email = "test@example.com"

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # confirm via GET too
    get_resp = client.get("/activities")
    assert email in get_resp.json()[activity]["participants"]


def test_signup_duplicate_fails(client):
    activity = "Chess Club"
    email = "dup@example.com"

    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400
    assert "already signed up" in r2.json()["detail"].lower()


def test_signup_nonexistent_activity(client):
    resp = client.post("/activities/NoClub/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_remove_participant_success(client):
    activity = "Chess Club"
    email = "rm@example.com"

    client.post(f"/activities/{activity}/signup", params={"email": email})
    assert email in activities[activity]["participants"]

    rdel = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert rdel.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_nonexistent_activity(client):
    resp = client.delete("/activities/NoClub/participants", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_remove_unregistered_participant(client):
    activity = "Chess Club"
    resp = client.delete(f"/activities/{activity}/participants", params={"email": "noone@x.com"})
    assert resp.status_code == 404
