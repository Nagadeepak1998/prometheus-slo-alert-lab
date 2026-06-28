from __future__ import annotations

import json
from pathlib import Path

from prometheus_slo_alert_lab.models import ScenarioReport, SloEvaluationReport


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
