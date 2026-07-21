from __future__ import annotations

from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.models import (
    AlertRoute,
    RoutedAlert,
    RoutingDecision,
    RoutingReviewReport,
    Severity,
    SloConfig,
)


def review_alert_routing(
    config: SloConfig, raw_metrics: list[dict], routes: list[AlertRoute]
) -> RoutingReviewReport:
    evaluation = evaluate_slos(config, raw_metrics)
    routes_by_service = {route.service: route for route in routes}
    alerts: list[RoutedAlert] = []
    findings: list[str] = []

    for policy in evaluation.policies:
        if not policy.triggered:
            continue
        route = routes_by_service.get(policy.service)
        missing = _missing_fields(policy.severity, route)
        if missing:
            findings.append(
                f"{policy.service} {policy.policy} lacks routing fields: {', '.join(missing)}."
            )
        alerts.append(
            RoutedAlert(
                service=policy.service,
                slo=policy.slo,
                policy=policy.policy,
                severity=policy.severity,
                owner=route.owner if route else None,
                destination=_destination(policy.severity, route),
                runbook_url=route.runbook_url if route else None,
                escalation_policy=route.escalation_policy if route else None,
                covered=not missing,
            )
        )

    covered = sum(alert.covered for alert in alerts)
    coverage = round(covered / len(alerts) * 100, 1) if alerts else 100.0
    return RoutingReviewReport(
        decision=RoutingDecision.ready if not findings else RoutingDecision.blocked,
        triggered_alerts=len(alerts),
        covered_alerts=covered,
        coverage_percent=coverage,
        alerts=alerts,
        findings=findings,
    )


def _missing_fields(severity: Severity, route: AlertRoute | None) -> list[str]:
    if route is None:
        return ["route"]
    required = {
        "owner": route.owner,
        "destination": route.page_channel if severity == Severity.page else route.ticket_queue,
        "runbook_url": route.runbook_url,
    }
    if severity == Severity.page:
        required["escalation_policy"] = route.escalation_policy
    return [name for name, value in required.items() if not value]


def _destination(severity: Severity, route: AlertRoute | None) -> str | None:
    if route is None:
        return None
    return route.page_channel if severity == Severity.page else route.ticket_queue
