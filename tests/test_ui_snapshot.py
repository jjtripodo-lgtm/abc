from pathlib import Path


def test_index_snapshot(client):
    response = client.get("/")
    assert response.status_code == 200

    snapshot_path = Path(__file__).resolve().parent / "snapshots" / "index.html"
    expected = snapshot_path.read_text().strip()
    assert response.text.strip() == expected
