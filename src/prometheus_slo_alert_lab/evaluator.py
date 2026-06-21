from __future__ import annotations

from collections import defaultdict

from prometheus_slo_alert_lab.models import (
    PolicyEvaluation,
    Severity,
    SloConfig,
    SloEvaluationReport,
    WindowEvaluation,
    WindowMetric,
)


SEVERITY_RANK = {Severity.ok: 0, Severity.ticket: 1, Severity.page: 2}


def evaluate_slos(config: SloConfig, raw_metrics: list[dict]) -> SloEvaluationReport:
    metrics = [WindowMetric.model_validate(item) for item in raw_metrics]
    target_by_key = {(target.service, target.slo): target for target in config.targets}
    metrics_by_key: dict[tuple[str, str, str], WindowMetric] = {
        (metric.service, metric.slo, metric.window): metric for metric in metrics
    }

    window_evaluations: list[WindowEvaluation] = []
    window_burn_rates: dict[tuple[str, str, str], float] = {}

    for metric in metrics:
        target = target_by_key.get((metric.service, metric.slo))
        if target is None:
            continue
        error_rate = metric.bad_events / metric.total_events if metric.total_events else 0.0
        burn_rate = error_rate / target.error_budget_ratio if target.error_budget_ratio else 0.0
        window_burn_rates[(metric.service, metric.slo, metric.window)] = burn_rate
        window_evaluations.append(
            WindowEvaluation(
                service=metric.service,
                slo=metric.slo,
                window=metric.window,
                total_events=metric.total_events,
                bad_events=metric.bad_events,
                error_rate=round(error_rate, 6),
                burn_rate=round(burn_rate, 3),
            )
        )

    policy_results: list[PolicyEvaluation] = []
    for target in config.targets:
        for policy in config.policies:
            short_key = (target.service, target.slo, policy.short_window)
            long_key = (target.service, target.slo, policy.long_window)
            if short_key not in metrics_by_key or long_key not in metrics_by_key:
                continue
            short_burn = window_burn_rates.get(short_key, 0.0)
            long_burn = window_burn_rates.get(long_key, 0.0)
            triggered = (
                short_burn >= policy.burn_rate_threshold
                and long_burn >= policy.burn_rate_threshold
            )
            policy_results.append(
                PolicyEvaluation(
                    policy=policy.name,
                    severity=policy.severity,
                    service=target.service,
                    slo=target.slo,
                    short_window=policy.short_window,
                    long_window=policy.long_window,
                    threshold=policy.burn_rate_threshold,
                    short_burn_rate=round(short_burn, 3),
                    long_burn_rate=round(long_burn, 3),
                    triggered=triggered,
                )
            )

    decision = _highest_triggered_severity(policy_results)
    return SloEvaluationReport(
        decision=decision,
        services_evaluated=len({(target.service, target.slo) for target in config.targets}),
        windows=sorted(window_evaluations, key=lambda item: (item.service, item.slo, item.window)),
        policies=sorted(
            policy_results,
            key=lambda item: (not item.triggered, -SEVERITY_RANK[item.severity], item.service),
        ),
        recommendations=_recommend(policy_results),
    )


def _highest_triggered_severity(results: list[PolicyEvaluation]) -> Severity:
    severity = Severity.ok
    for result in results:
        if result.triggered and SEVERITY_RANK[result.severity] > SEVERITY_RANK[severity]:
            severity = result.severity
    return severity


def _recommend(results: list[PolicyEvaluation]) -> list[str]:
    triggered_by_service: dict[tuple[str, str], list[PolicyEvaluation]] = defaultdict(list)
    for result in results:
        if result.triggered:
            triggered_by_service[(result.service, result.slo)].append(result)

    if not triggered_by_service:
        return ["No SLO policy breached. Keep monitoring current windows."]

    recommendations: list[str] = []
    for (service, slo), policies in sorted(triggered_by_service.items()):
        severities = {policy.severity for policy in policies}
        if Severity.page in severities:
            recommendations.append(
                f"Page on-call for {service} {slo}; freeze rollout and inspect recent deploys."
            )
        else:
            recommendations.append(
                f"Open ticket for {service} {slo}; review burn trend before next release window."
            )
    return recommendations
