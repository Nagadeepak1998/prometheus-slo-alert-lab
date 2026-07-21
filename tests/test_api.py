from fastapi.testclient import TestClient

from prometheus_slo_alert_lab.api import app
from prometheus_slo_alert_lab.config import (
    load_config,
    load_history,
    load_metrics,
    load_routes,
    load_scenario,
)


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


def test_simulate_endpoint_returns_page_scenario():
    client = TestClient(app)
    payload = {
        "config": load_config("examples/slo_config.yaml").model_dump(mode="json"),
        "stages": load_scenario("examples/incident_scenario.json"),
    }

    response = client.post("/simulate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "page"
    assert body["stages"][1]["name"] == "checkout deploy regression"
    assert body["recommendations"][0] == (
        "First page-worthy stage is checkout deploy regression at +20 minutes."
    )


def test_history_endpoint_returns_page_review():
    client = TestClient(app)
    payload = {
        "config": load_config("examples/slo_config.yaml").model_dump(mode="json"),
        "windows": load_history("examples/deploy_history.json"),
    }

    response = client.post("/history", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "page"
    assert body["page_windows"] == 1
    assert body["worst_window"] == "post-expansion incident review"


def test_routing_endpoint_returns_ready_coverage_review():
    client = TestClient(app)
    payload = {
        "config": load_config("examples/slo_config.yaml").model_dump(mode="json"),
        "metrics": load_metrics("examples/window_metrics.json"),
        "routes": [
            route.model_dump(mode="json") for route in load_routes("examples/alert_routes.yaml")
        ],
    }

    response = client.post("/routing/review", json=payload)

    assert response.status_code == 200
    assert response.json()["decision"] == "ready"
    assert response.json()["coverage_percent"] == 100.0
