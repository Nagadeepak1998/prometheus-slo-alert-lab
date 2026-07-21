from __future__ import annotations

import json
from pathlib import Path

from prometheus_slo_alert_lab.models import (
    HistoryReviewReport,
    RoutingReviewReport,
    ScenarioReport,
    SloEvaluationReport,
)


def write_report(report: SloEvaluationReport, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "slo_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    (path / "slo_report.md").write_text(render_markdown(report), encoding="utf-8")


def write_scenario_report(report: ScenarioReport, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "scenario_report.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    (path / "scenario_report.md").write_text(render_scenario_markdown(report), encoding="utf-8")


def write_history_report(report: HistoryReviewReport, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "history_review.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    (path / "history_review.md").write_text(render_history_markdown(report), encoding="utf-8")


def write_routing_report(report: RoutingReviewReport, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "routing_review.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8"
    )
    (path / "routing_review.md").write_text(render_routing_markdown(report), encoding="utf-8")


def render_markdown(report: SloEvaluationReport) -> str:
    lines = [
        "# SLO Burn-Rate Report",
        "",
        f"Decision: **{report.decision.value.upper()}**",
        "",
        "## Triggered Policies",
        "",
    ]
    triggered = [policy for policy in report.policies if policy.triggered]
    if triggered:
        lines.append("| Service | SLO | Policy | Severity | Short Burn | Long Burn |")
        lines.append("|---|---|---|---|---:|---:|")
        for policy in triggered:
            lines.append(
                "| "
                f"{policy.service} | {policy.slo} | {policy.policy} | "
                f"{policy.severity.value} | {policy.short_burn_rate} | "
                f"{policy.long_burn_rate} |"
            )
    else:
        lines.append("No policies triggered.")

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report.recommendations)
    lines.append("")
    return "\n".join(lines)


def render_scenario_markdown(report: ScenarioReport) -> str:
    lines = [
        "# SLO Incident Scenario Report",
        "",
        f"Decision: **{report.decision.value.upper()}**",
        "",
        "## Stage Timeline",
        "",
    ]
    if report.stages:
        lines.append("| Stage | Time | Decision | Triggered Policies | Max Burn Rate |")
        lines.append("|---|---:|---|---:|---:|")
        for stage in report.stages:
            lines.append(
                "| "
                f"{stage.name} | +{stage.minutes_from_start}m | {stage.decision.value} | "
                f"{stage.triggered_policies} | {stage.max_burn_rate} |"
            )
    else:
        lines.append("No scenario stages were evaluated.")

    lines.extend(["", "## Incident Handoff", ""])
    lines.extend(f"- {item}" for item in report.recommendations)
    lines.append("")
    return "\n".join(lines)


def render_history_markdown(report: HistoryReviewReport) -> str:
    lines = [
        "# SLO History Review",
        "",
        f"Decision: **{report.decision.value.upper()}**",
        "",
        "## Release Windows",
        "",
    ]
    if report.windows:
        lines.append(
            "| Window | Deploy | Minutes Since Deploy | Decision | Triggered Policies | Max Burn | Page Policy |"
        )
        lines.append("|---|---|---:|---|---:|---:|---|")
        for window in report.windows:
            lines.append(
                "| "
                f"{window.name} | {window.deploy_ref} | {window.minutes_since_deploy} | "
                f"{window.decision.value} | {window.triggered_policies} | "
                f"{window.max_burn_rate} | {window.page_policy or '-'} |"
            )
    else:
        lines.append("No history windows were evaluated.")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Windows evaluated: {report.windows_evaluated}",
            f"- Page windows: {report.page_windows}",
            f"- Ticket windows: {report.ticket_windows}",
            f"- Worst window: {report.worst_window or '-'}",
            f"- Max burn rate: {report.max_burn_rate}",
            "",
            "## Recommendations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report.recommendations)
    lines.append("")
    return "\n".join(lines)


def render_routing_markdown(report: RoutingReviewReport) -> str:
    lines = [
        "# Alert Routing Coverage Review",
        "",
        f"Decision: **{report.decision.value.upper()}**",
        "",
        f"Coverage: **{report.coverage_percent}%** ({report.covered_alerts}/{report.triggered_alerts})",
        "",
        "## Triggered Alert Evidence",
        "",
    ]
    if report.alerts:
        lines.extend(
            [
                "| Service | SLO | Policy | Severity | Owner | Destination | Runbook | Escalation | Covered |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for alert in report.alerts:
            lines.append(
                f"| {alert.service} | {alert.slo} | {alert.policy} | {alert.severity.value} | "
                f"{alert.owner or '-'} | {alert.destination or '-'} | {alert.runbook_url or '-'} | "
                f"{alert.escalation_policy or '-'} | {'yes' if alert.covered else 'no'} |"
            )
    else:
        lines.append("No alert policies triggered.")
    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {finding}" for finding in report.findings)
    if not report.findings:
        lines.append("- Every triggered alert has an accountable owner and actionable route.")
    lines.append("")
    return "\n".join(lines)
