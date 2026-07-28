from fastapi.testclient import TestClient

import server


def test_subscription_validation_echoes_challenge(monkeypatch):
    monkeypatch.setenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "expected-token")
    client = TestClient(server.app)

    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "expected-token",
            "hub.challenge": "challenge-value",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"hub.challenge": "challenge-value"}


def test_subscription_validation_rejects_bad_token(monkeypatch):
    monkeypatch.setenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "expected-token")
    client = TestClient(server.app)

    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "challenge-value",
        },
    )

    assert response.status_code == 403


def test_create_activity_event_is_acknowledged_and_processed(monkeypatch):
    processed_activity_ids = []
    monkeypatch.setattr(
        server,
        "process_created_activity",
        lambda activity_id: processed_activity_ids.append(activity_id),
    )
    client = TestClient(server.app)

    response = client.post(
        "/webhook",
        json={
            "object_type": "activity",
            "aspect_type": "create",
            "object_id": 12345,
            "owner_id": 1,
            "subscription_id": 2,
            "event_time": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    assert processed_activity_ids == [12345]


def test_irrelevant_event_is_acknowledged_without_processing(monkeypatch):
    monkeypatch.setattr(
        server,
        "process_created_activity",
        lambda activity_id: (_ for _ in ()).throw(AssertionError("must not process")),
    )
    client = TestClient(server.app)

    response = client.post(
        "/webhook",
        json={"object_type": "activity", "aspect_type": "update", "object_id": 12345},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
