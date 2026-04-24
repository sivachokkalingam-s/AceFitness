import sqlite3
import pytest
import logic


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(logic, "DB_NAME", str(db_path))
    logic.init_db()
    return str(db_path)


def test_save_client(temp_db):
    calories = logic.save_client("Siva", 25, 70, "Fat Loss (FL)")
    assert calories == 1540

    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT name, age, weight, program, calories FROM clients WHERE name = ?",
        ("Siva",)
    ).fetchone()
    conn.close()

    assert row == ("Siva", 25, 70.0, "Fat Loss (FL)", 1540)


def test_load_client(temp_db):
    logic.save_client("Siva", 25, 70, "Fat Loss (FL)")
    data = logic.load_client("Siva")

    assert data == {
        "name": "Siva",
        "age": 25,
        "weight": 70.0,
        "program": "Fat Loss (FL)",
        "calories": 1540,
    }


def test_invalid_client(temp_db):
    assert logic.load_client("Unknown") is None


def test_save_progress(temp_db):
    logic.save_client("Siva", 25, 70, "Fat Loss (FL)")
    logic.save_progress("Siva", 80)

    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT client_name, adherence FROM progress WHERE client_name = ?",
        ("Siva",)
    ).fetchone()
    conn.close()

    assert row == ("Siva", 80)


def test_save_client_missing_required(temp_db):
    with pytest.raises(ValueError):
        logic.save_client("", 25, 70, "")
