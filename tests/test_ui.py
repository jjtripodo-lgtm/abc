
def test_ui_structure_and_reason_badges(client):
    response = client.get("/?demo=1")
    assert response.status_code == 200
    html = response.text

    assert "Peter Lynch Stock Screener" in html
    assert "screen-form" in html
    assert "export-json" in html
    assert "export-csv" in html
    assert "reason-badge" in html
    assert "Reason codes" in html
    assert "threshold=" in html
