from __future__ import annotations

from prometheus_slo_alert_lab.evaluator import SEVERITY_RANK, evaluate_slos
from prometheus_slo_alert_lab.models import (
    HistoryReviewReport,
    HistoryWindow,
    HistoryWindowEvaluation,
    Severity,
    SloConfig,
    SloEvaluationReport,
)


def review_slo_history(config: SloConfig, raw_windows: list[dict]) -> HistoryReviewReport:
    windows = [HistoryWindow.model_validate(item) for item in raw_windows]
    evaluations: list[HistoryWindowEvaluation] = []

    for window in sorted(windows, key=lambda item: item.minutes_since_deploy):
        report = evaluate_slos(config, window.metrics)
        evaluations.append(
            HistoryWindowEvaluation(
                name=window.name,
                deploy_ref=window.deploy_ref,
                minutes_since_deploy=window.minutes_since_deploy,
                decision=report.decision,
                triggered_policies=sum(1 for policy in report.policies if policy.triggered),
                max_burn_rate=_max_burn_rate(report),
                page_policy=_first_page_policy(report),
            )
        )

    decision = _highest_window_severity(evaluations)
    worst_window = max(evaluations, key=lambda item: item.max_burn_rate, default=None)
    return HistoryReviewReport(
        decision=decision,
        windows_evaluated=len(evaluations),
        page_windows=sum(1 for item in evaluations if item.decision == Severity.page),
        ticket_windows=sum(1 for item in evaluations if item.decision == Severity.ticket),
        worst_window=worst_window.name if worst_window else None,
        max_burn_rate=worst_window.max_burn_rate if worst_window else 0.0,
        windows=evaluations,
        recommendations=_history_recommendations(evaluations),
    )


def _max_burn_rate(report: SloEvaluationReport) -> float:
    if not report.windows:
        return 0.0
    return max(window.burn_rate for window in report.windows)


def _first_page_policy(report: SloEvaluationReport) -> str | None:
    for policy in report.policies:
        if policy.triggered and policy.severity == Severity.page:
            return policy.policy
    return None


def _highest_window_severity(windows: list[HistoryWindowEvaluation]) -> Severity:
    severity = Severity.ok
    for window in windows:
        if SEVERITY_RANK[window.decision] > SEVERITY_RANK[severity]:
            severity = window.decision
    return severity


def _history_recommendations(windows: list[HistoryWindowEvaluation]) -> list[str]:
    if not windows:
        return ["No history windows were provided."]

    page_windows = [window for window in windows if window.decision == Severity.page]
    if page_windows:
        first = page_windows[0]
        return [
            f"First page-worthy history window is {first.name} for deploy {first.deploy_ref}.",
            "Block promotion until rollback, mitigation, or an explicit incident owner is recorded.",
        ]

    ticket_windows = [window for window in windows if window.decision == Severity.ticket]
    if ticket_windows:
        return [
            f"{len(ticket_windows)} history window(s) require follow-up ticket review.",
            "Keep the release under observation before increasing rollout percentage.",
        ]

    return ["History remains within SLO policy; promotion can continue with normal monitoring."]
