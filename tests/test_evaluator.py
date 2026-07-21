from prometheus_slo_alert_lab.config import (
    load_config,
    load_history,
    load_metrics,
    load_routes,
    load_scenario,
)
from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.history import review_slo_history
from prometheus_slo_alert_lab.models import Severity
from prometheus_slo_alert_lab.reports import (
    render_history_markdown,
    render_routing_markdown,
    render_scenario_markdown,
)
from prometheus_slo_alert_lab.routing import review_alert_routing
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
        {
            "service": "checkout-api",
            "slo": "availability",
            "window": "5m",
            "total_events": 10000,
            "bad_events": 1,
        },
        {
            "service": "checkout-api",
            "slo": "availability",
            "window": "30m",
            "total_events": 60000,
            "bad_events": 4,
        },
        {
            "service": "checkout-api",
            "slo": "availability",
            "window": "1h",
            "total_events": 120000,
            "bad_events": 8,
        },
        {
            "service": "checkout-api",
            "slo": "availability",
            "window": "6h",
            "total_events": 720000,
            "bad_events": 40,
        },
        {
            "service": "recommender-api",
            "slo": "availability",
            "window": "5m",
            "total_events": 8000,
            "bad_events": 1,
        },
        {
            "service": "recommender-api",
            "slo": "availability",
            "window": "30m",
            "total_events": 48000,
            "bad_events": 4,
        },
        {
            "service": "recommender-api",
            "slo": "availability",
            "window": "1h",
            "total_events": 96000,
            "bad_events": 8,
        },
        {
            "service": "recommender-api",
            "slo": "availability",
            "window": "6h",
            "total_events": 576000,
            "bad_events": 40,
        },
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


def test_history_review_identifies_first_page_window():
    config = load_config("examples/slo_config.yaml")

    report = review_slo_history(config, load_history("examples/deploy_history.json"))

    assert report.decision == Severity.page
    assert report.windows_evaluated == 3
    assert report.page_windows == 1
    assert report.ticket_windows == 1
    assert report.worst_window == "post-expansion incident review"
    assert report.recommendations[0] == (
        "First page-worthy history window is post-expansion incident review "
        "for deploy checkout-2026.07.08-3."
    )


def test_history_markdown_is_release_review_ready():
    config = load_config("examples/slo_config.yaml")
    report = review_slo_history(config, load_history("examples/deploy_history.json"))

    markdown = render_history_markdown(report)

    assert "# SLO History Review" in markdown
    assert (
        "| post-expansion incident review | checkout-2026.07.08-3 | 40 | page | 2 | 22.0 | fast-page |"
        in markdown
    )
    assert "Block promotion until rollback" in markdown


def test_routing_review_covers_triggered_alerts():
    report = review_alert_routing(
        load_config("examples/slo_config.yaml"),
        load_metrics("examples/window_metrics.json"),
        load_routes("examples/alert_routes.yaml"),
    )

    assert report.decision.value == "ready"
    assert report.triggered_alerts == 2
    assert report.covered_alerts == 2
    assert report.coverage_percent == 100.0
    assert report.alerts[0].owner == "checkout-platform"


def test_routing_review_blocks_missing_page_escalation():
    report = review_alert_routing(
        load_config("examples/slo_config.yaml"),
        load_metrics("examples/window_metrics.json"),
        load_routes("examples/incomplete_alert_routes.yaml"),
    )

    assert report.decision.value == "blocked"
    assert report.coverage_percent == 50.0
    assert report.findings == ["checkout-api fast-page lacks routing fields: escalation_policy."]


def test_routing_markdown_contains_incident_ownership_evidence():
    report = review_alert_routing(
        load_config("examples/slo_config.yaml"),
        load_metrics("examples/window_metrics.json"),
        load_routes("examples/alert_routes.yaml"),
    )

    markdown = render_routing_markdown(report)

    assert "Coverage: **100.0%** (2/2)" in markdown
    assert "pagerduty:checkout-primary" in markdown
    assert "checkout-primary-to-platform-manager" in markdown
