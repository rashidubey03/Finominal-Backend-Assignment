from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "portfolio-optimizer-api",
        "version": "0.1.0",
    }


def test_data_summary() -> None:
    response = client.get("/data/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["fund_count"] == 5
    assert body["tickers"] == ["AGG", "GLD", "IEFA", "SPY", "VEA"]
    assert body["factors"] == ["momentum", "size", "value"]

