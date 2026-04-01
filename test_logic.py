import logic
import os


def setup_module():
    # fresh DB before tests
    if os.path.exists("aceest_fitness.db"):
        os.remove("aceest_fitness.db")
    logic.init_db()


def test_save_client():
    calories = logic.save_client("Siva", 25, 70, "Fat Loss (FL)")
    assert calories == 1540   # 70 * 22


def test_load_client():
    data = logic.load_client("Siva")
    assert data is not None
    assert data["name"] == "Siva"


def test_invalid_client():
    data = logic.load_client("Unknown")
    assert data is None


def test_save_progress():
    logic.save_progress("Siva", 80)
    assert True   # if no error → pass
