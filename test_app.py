import sqlite3
import logic
from Aceestver import app


def test_homepage():
    app.config["TESTING"] = True
    with app.test_client() as client:
        resp = client.get("/")

    assert resp.status_code == 200
    assert b"ACEest Functional Fitness System" in resp.data


def test_api_save_and_load_client(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()

    app.config["TESTING"] = True
    with app.test_client() as client:
        payload = {
            "name": "Alex",
            "age": 30,
            "weight": 80,
            "program": "Muscle Gain (MG)"
        }
        save_resp = client.post("/client", json=payload)
        assert save_resp.status_code == 200
        assert save_resp.get_json() == 2800

        load_resp = client.get("/client/Alex")
        assert load_resp.status_code == 200
        assert load_resp.get_json() == {
            "name": "Alex",
            "age": 30,
            "weight": 80.0,
            "program": "Muscle Gain (MG)",
            "calories": 2800,
        }


def test_api_load_missing_client(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()

    app.config["TESTING"] = True
    with app.test_client() as client:
        resp = client.get("/client/NoSuchClient")

    assert resp.status_code == 200
    assert resp.get_json() is None


def test_api_save_progress(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()
    logic.save_client("Taylor", 27, 65, "Beginner (BG)")

    app.config["TESTING"] = True
    with app.test_client() as client:
        resp = client.post("/progress", json={"name": "Taylor", "adherence": 90})

    assert resp.status_code == 200
    assert resp.get_json() is None

    conn = sqlite3.connect(str(db_path))
    row = conn.execute(
        "SELECT client_name, adherence FROM progress WHERE client_name = ?",
        ("Taylor",)
    ).fetchone()
    conn.close()

    assert row == ("Taylor", 90)


def test_save_client_form_route(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()

    app.config["TESTING"] = True
    with app.test_client() as client:
        resp = client.post("/save_client", data={
            "name": "Jess",
            "age": "28",
            "weight": "65",
            "program": "Beginner (BG)",
        })

    assert resp.status_code == 200
    assert b"ACEest Functional Fitness System" in resp.data


def test_load_client_form_route(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()
    logic.save_client("Jordan", 29, 75, "Fat Loss (FL)")

    app.config["TESTING"] = True
    with app.test_client() as client:
        resp = client.post("/load_client", data={"name": "Jordan"})

    assert resp.status_code == 200
    assert b"CLIENT PROFILE" in resp.data
    assert b"Jordan" in resp.data
