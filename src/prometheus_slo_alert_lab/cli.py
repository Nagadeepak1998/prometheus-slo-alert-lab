from __future__ import annotations

import argparse
import json

from prometheus_slo_alert_lab.config import load_config, load_history, load_metrics, load_scenario
from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.history import review_slo_history
from prometheus_slo_alert_lab.reports import write_history_report, write_report, write_scenario_report
from prometheus_slo_alert_lab.scenario import simulate_scenario


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Prometheus-style SLO burn rates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--config", required=True)
    evaluate.add_argument("--metrics", required=True)
    evaluate.add_argument("--out", default="reports/latest")
    evaluate.add_argument("--fail-on-page", action="store_true")

    simulate = subparsers.add_parser("simulate")
    simulate.add_argument("--config", required=True)
    simulate.add_argument("--scenario", required=True)
    simulate.add_argument("--out", default="reports/scenario")
    simulate.add_argument("--fail-on-page", action="store_true")

    history = subparsers.add_parser("history")
    history.add_argument("--config", required=True)
    history.add_argument("--history", required=True)
    history.add_argument("--out", default="reports/history")
    history.add_argument("--fail-on-page", action="store_true")

    args = parser.parse_args()
    if args.command == "evaluate":
        config = load_config(args.config)
        report = evaluate_slos(config, load_metrics(args.metrics))
        write_report(report, args.out)
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return 2 if args.fail_on_page and report.decision.value == "page" else 0
    if args.command == "simulate":
        config = load_config(args.config)
        report = simulate_scenario(config, load_scenario(args.scenario))
        write_scenario_report(report, args.out)
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return 2 if args.fail_on_page and report.decision.value == "page" else 0
    if args.command == "history":
        config = load_config(args.config)
        report = review_slo_history(config, load_history(args.history))
        write_history_report(report, args.out)
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return 2 if args.fail_on_page and report.decision.value == "page" else 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
