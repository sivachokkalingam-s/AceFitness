"""
test_logic.py – Unit tests for ACEest Fitness & Gym logic layer
Assignment 2 extended test suite (Pytest + Coverage)
"""
import pytest
import os
import sqlite3
import logic

# Patch DB name before importing logic so tests use an in-memory / temp DB
os.environ.setdefault("TESTING", "1")

TEST_DB = "test_aceest.db"


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Each test gets a fresh SQLite DB in a temp directory."""
    db_path = str(tmp_path / "aceest_fitness.db")
    monkeypatch.setattr(logic, "DB_NAME", db_path)
    logic.init_db()
    yield db_path


# ──────────────────────────────────────────────
# init_db
# ──────────────────────────────────────────────

class TestInitDb:
    def test_creates_clients_table(self, isolated_db):
        conn = sqlite3.connect(isolated_db)
        cur = conn.cursor()
        query = (
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='clients'"
        )
        cur.execute(query)
        assert cur.fetchone() is not None
        conn.close()

    def test_creates_progress_table(self, isolated_db):
        conn = sqlite3.connect(isolated_db)
        cur = conn.cursor()
        query = (
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='progress'"
        )
        cur.execute(query)
        assert cur.fetchone() is not None
        conn.close()

    def test_idempotent(self, isolated_db):
        """Calling init_db twice should not raise."""
        logic.init_db()


# ──────────────────────────────────────────────
# save_client
# ──────────────────────────────────────────────

class TestSaveClient:
    def test_fat_loss_calories(self):
        cals = logic.save_client("Alice", 25, 70, "Fat Loss (FL)")
        assert cals == 70 * 22  # 1540

    def test_muscle_gain_calories(self):
        cals = logic.save_client("Bob", 30, 80, "Muscle Gain (MG)")
        assert cals == 80 * 35  # 2800

    def test_beginner_calories(self):
        cals = logic.save_client("Carol", 22, 60, "Beginner (BG)")
        assert cals == 60 * 26  # 1560

    def test_returns_integer(self):
        cals = logic.save_client("Dave", 28, 75.5, "Fat Loss (FL)")
        assert isinstance(cals, int)

    def test_missing_name_raises(self):
        with pytest.raises(ValueError, match="Name and Program required"):
            logic.save_client("", 25, 70, "Fat Loss (FL)")

    def test_missing_program_raises(self):
        with pytest.raises(ValueError, match="Name and Program required"):
            logic.save_client("Eve", 25, 70, "")

    def test_invalid_program_raises(self):
        with pytest.raises(KeyError):
            logic.save_client("Frank", 25, 70, "Invalid Program")

    def test_upsert_same_name(self):
        logic.save_client("Grace", 25, 60, "Fat Loss (FL)")
        cals = logic.save_client("Grace", 25, 80, "Muscle Gain (MG)")
        client = logic.load_client("Grace")
        assert client["calories"] == cals
        assert client["program"] == "Muscle Gain (MG)"


# ──────────────────────────────────────────────
# load_client
# ──────────────────────────────────────────────

class TestLoadClient:
    def test_load_existing_client(self):
        logic.save_client("Hank", 35, 90, "Muscle Gain (MG)")
        client = logic.load_client("Hank")
        assert client is not None
        assert client["name"] == "Hank"
        assert client["age"] == 35
        assert client["weight"] == 90
        assert client["program"] == "Muscle Gain (MG)"
        assert client["calories"] == 90 * 35

    def test_load_nonexistent_returns_none(self):
        result = logic.load_client("NoSuchPerson")
        assert result is None

    def test_load_returns_dict(self):
        logic.save_client("Iris", 28, 65, "Beginner (BG)")
        client = logic.load_client("Iris")
        assert isinstance(client, dict)
        expected_keys = {"name", "age", "weight", "program", "calories"}
        assert set(client.keys()) == expected_keys


# ──────────────────────────────────────────────
# save_progress
# ──────────────────────────────────────────────

class TestSaveProgress:
    def test_saves_without_error(self):
        logic.save_client("Jake", 30, 75, "Fat Loss (FL)")
        logic.save_progress("Jake", 85)  # should not raise

    def test_multiple_progress_entries(self, isolated_db):
        logic.save_client("Kate", 26, 68, "Beginner (BG)")
        logic.save_progress("Kate", 70)
        logic.save_progress("Kate", 90)
        conn = sqlite3.connect(isolated_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM progress WHERE client_name='Kate'")
        count = cur.fetchone()[0]
        conn.close()
        assert count == 2

    def test_adherence_stored_correctly(self, isolated_db):
        logic.save_client("Liam", 24, 72, "Muscle Gain (MG)")
        logic.save_progress("Liam", 95)
        conn = sqlite3.connect(isolated_db)
        cur = conn.cursor()
        cur.execute("SELECT adherence FROM progress WHERE client_name='Liam'")
        row = cur.fetchone()
        conn.close()
        assert row[0] == 95


# ──────────────────────────────────────────────
# PROGRAMS constant
# ──────────────────────────────────────────────

class TestPrograms:
    def test_all_three_programs_exist(self):
        assert "Fat Loss (FL)" in logic.PROGRAMS
        assert "Muscle Gain (MG)" in logic.PROGRAMS
        assert "Beginner (BG)" in logic.PROGRAMS

    def test_programs_have_factor(self):
        for name, data in logic.PROGRAMS.items():
            assert "factor" in data, f"{name} missing 'factor'"
            assert isinstance(data["factor"], (int, float))
