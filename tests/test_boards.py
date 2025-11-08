from .utils import count_clues, is_board_str


def test_random_board_default_medium(client):
    r = client.get("/boards/random")
    assert r.status_code == 200
    data = r.json()
    assert is_board_str(data["initial_board"])
    assert is_board_str(data["solution_board"])
    assert count_clues(data["solution_board"]) == 81


def test_create_and_get_board(client):
    payload = {
        "public_id": "test-public-123",
        "difficulty": "MEDIUM",
        "initial_board": "0" * 81,
        "solution_board": "1" * 81,
    }
    r = client.post("/boards", json=payload)
    assert r.status_code in (200, 201)
    created = r.json()
    board_id = created["id"]

    r2 = client.get(f"/boards/{board_id}")
    assert r2.status_code == 200
    fetched = r2.json()
    assert fetched["id"] == board_id
    assert fetched["public_id"] == "test-public-123"
