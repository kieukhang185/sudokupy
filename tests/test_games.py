from tests.utils import is_board_str


def test_games_new(client):
    r = client.post("/games/new", json={"difficulty": "40"})
    assert r.status_code == 200
    data = r.json()
    assert is_board_str(data["puzzle"])
    assert is_board_str(data["solution"])


def test_games_validate_and_solve(client):
    r = client.post("/games/new", json={"difficulty": "40"})
    assert r.status_code == 200
    data = r.json()
    puzzle = data["puzzle"]
    solution = data["solution"]

    r2 = client.post(
        "/games/validate", json={"board": {"puzzle": puzzle, "state": puzzle}}
    )
    assert r2.status_code == 200
    vr = r2.json()
    assert vr["valid"] is True
    assert vr["complete"] is False

    r3 = client.post(
        "/games/solve", json={"board": {"puzzle": puzzle, "state": puzzle}}
    )
    assert r3.status_code == 200
    sr = r3.json()
    assert is_board_str(sr["solution"])

    r4 = client.post(
        "/games/validate", json={"board": {"puzzle": solution, "state": solution}}
    )
    assert r4.status_code == 200
    vr2 = r4.json()
    assert vr2["valid"] is True
    assert vr2["complete"] is True
