from prometheus_slo_alert_lab.config import load_config, load_metrics, load_scenario
from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.models import Severity
from prometheus_slo_alert_lab.reports import render_scenario_markdown
from prometheus_slo_alert_lab.scenario import simulate_scenario


def test_evaluator_pages_when_short_and_long_windows_breach():
    config = load_config("examples/slo_config.yaml")
    report = evaluate_slos(config, load_metrics("examples/window_metrics.json"))

    assert report.decision == Severity.page
    assert any(policy.triggered and policy.severity == Severity.page for policy in report.policies)
    assert any("checkout-api" in item for item in report.recommendations)


def test_evaluator_stays_ok_for_healthy_metrics():
    config = load_config("examples/slo_config.yaml")
    healthy = [
        {"service": "checkout-api", "slo": "availability", "window": "5m", "total_events": 10000, "bad_events": 1},
        {"service": "checkout-api", "slo": "availability", "window": "30m", "total_events": 60000, "bad_events": 4},
        {"service": "checkout-api", "slo": "availability", "window": "1h", "total_events": 120000, "bad_events": 8},
        {"service": "checkout-api", "slo": "availability", "window": "6h", "total_events": 720000, "bad_events": 40},
        {"service": "recommender-api", "slo": "availability", "window": "5m", "total_events": 8000, "bad_events": 1},
        {"service": "recommender-api", "slo": "availability", "window": "30m", "total_events": 48000, "bad_events": 4},
        {"service": "recommender-api", "slo": "availability", "window": "1h", "total_events": 96000, "bad_events": 8},
        {"service": "recommender-api", "slo": "availability", "window": "6h", "total_events": 576000, "bad_events": 40},
    ]

    report = evaluate_slos(config, healthy)

    assert report.decision == Severity.ok
    assert report.recommendations == ["No SLO policy breached. Keep monitoring current windows."]


def test_scenario_simulation_identifies_first_page_stage():
    config = load_config("examples/slo_config.yaml")

    report = simulate_scenario(config, load_scenario("examples/incident_scenario.json"))

    assert report.decision == Severity.page
    assert [stage.name for stage in report.stages] == [
        "baseline before deploy",
        "checkout deploy regression",
        "rollback recovery",
    ]
    assert report.stages[1].decision == Severity.page
    assert report.stages[1].triggered_policies == 2
    assert report.recommendations[0] == (
        "First page-worthy stage is checkout deploy regression at +20 minutes."
    )


def test_scenario_markdown_is_incident_ready():
    config = load_config("examples/slo_config.yaml")
    report = simulate_scenario(config, load_scenario("examples/incident_scenario.json"))

    markdown = render_scenario_markdown(report)

    assert "# SLO Incident Scenario Report" in markdown
    assert "| checkout deploy regression | +20m | page | 2 | 22.0 |" in markdown
    assert "freeze risky releases" in markdown
