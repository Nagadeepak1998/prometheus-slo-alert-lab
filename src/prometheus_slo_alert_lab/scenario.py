from __future__ import annotations

from prometheus_slo_alert_lab.evaluator import SEVERITY_RANK, evaluate_slos
from prometheus_slo_alert_lab.models import (
    ScenarioReport,
    ScenarioStage,
    ScenarioStageEvaluation,
    Severity,
    SloConfig,
    SloEvaluationReport,
)


def simulate_scenario(config: SloConfig, raw_stages: list[dict]) -> ScenarioReport:
    stages = [ScenarioStage.model_validate(item) for item in raw_stages]
    evaluations: list[ScenarioStageEvaluation] = []

    for stage in sorted(stages, key=lambda item: item.minutes_from_start):
        report = evaluate_slos(config, stage.metrics)
        evaluations.append(
            ScenarioStageEvaluation(
                name=stage.name,
                minutes_from_start=stage.minutes_from_start,
                decision=report.decision,
                triggered_policies=sum(1 for policy in report.policies if policy.triggered),
                max_burn_rate=_max_burn_rate(report),
                recommendations=report.recommendations,
            )
        )

    decision = _highest_stage_severity(evaluations)
    return ScenarioReport(
        decision=decision,
        stages=evaluations,
        recommendations=_scenario_recommendations(evaluations),
    )


def _max_burn_rate(report: SloEvaluationReport) -> float:
    if not report.windows:
        return 0.0
    return max(window.burn_rate for window in report.windows)


def _highest_stage_severity(stages: list[ScenarioStageEvaluation]) -> Severity:
    severity = Severity.ok
    for stage in stages:
        if SEVERITY_RANK[stage.decision] > SEVERITY_RANK[severity]:
            severity = stage.decision
    return severity


def _scenario_recommendations(stages: list[ScenarioStageEvaluation]) -> list[str]:
    if not stages:
        return ["No scenario stages were provided."]

    pages = [stage for stage in stages if stage.decision == Severity.page]
    tickets = [stage for stage in stages if stage.decision == Severity.ticket]
    if pages:
        first = pages[0]
        return [
            f"First page-worthy stage is {first.name} at +{first.minutes_from_start} minutes.",
            "Use the stage timeline as the incident handoff and freeze risky releases.",
        ]
    if tickets:
        first = tickets[0]
        return [
            f"First ticket-worthy stage is {first.name} at +{first.minutes_from_start} minutes.",
            "Open follow-up work and keep the deploy window under observation.",
        ]
    return ["Scenario remains within SLO policy; no escalation is recommended."]
