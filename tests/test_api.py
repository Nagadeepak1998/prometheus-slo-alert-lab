from fastapi.testclient import TestClient

from prometheus_slo_alert_lab.api import app
from prometheus_slo_alert_lab.config import load_config, load_metrics


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_evaluate_endpoint_returns_page_decision():
    client = TestClient(app)
    payload = {
        "config": load_config("examples/slo_config.yaml").model_dump(mode="json"),
        "metrics": load_metrics("examples/window_metrics.json"),
    }

    response = client.post("/evaluate", json=payload)

    assert response.status_code == 200
    assert response.json()["decision"] == "page"


def test_metrics_endpoint_is_prometheus_compatible():
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "slo_alert_lab_evaluations_total" in response.text
