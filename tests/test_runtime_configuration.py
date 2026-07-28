import json

from fastapi.testclient import TestClient

import db
import req
import server


def test_database_path_can_be_configured_and_parent_directory_is_created(monkeypatch, tmp_path):
    database_path = tmp_path / "data" / "rideops.db"
    monkeypatch.setenv("RIDEOPS_DB_PATH", str(database_path))

    db.init_db()

    assert database_path.exists()


def test_token_file_path_can_be_configured(monkeypatch, tmp_path):
    token_path = tmp_path / "secrets" / "strava.json"
    token_path.parent.mkdir()
    token_state = {"access_token": "token", "refresh_token": "refresh", "expires_at": 9999999999}
    token_path.write_text(json.dumps(token_state), encoding="utf-8")
    monkeypatch.setenv("STRAVA_TOKEN_FILE", str(token_path))

    assert req.load_token_state() == token_state


def test_server_startup_initializes_configured_database(monkeypatch, tmp_path):
    database_path = tmp_path / "runtime" / "rideops.db"
    monkeypatch.setenv("RIDEOPS_DB_PATH", str(database_path))

    with TestClient(server.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert database_path.exists()
