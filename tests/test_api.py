
def test_hello_endpoint(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello screener"}


def test_screen_endpoint_returns_ranked_results(client):
    response = client.post(
        "/api/screen",
        json={"tickers": [], "risk_tolerance": "balanced", "universe": "stub"},
    )
    assert response.status_code == 200
    payload = response.json()
    results = payload["results"]
    assert len(results) >= 10
    scores = [item["score"] for item in results]
    assert scores == sorted(scores, reverse=True)
