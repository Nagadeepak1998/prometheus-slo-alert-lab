from __future__ import annotations

import argparse
import json

from prometheus_slo_alert_lab.config import load_config, load_metrics
from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.reports import write_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Prometheus-style SLO burn rates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--config", required=True)
    evaluate.add_argument("--metrics", required=True)
    evaluate.add_argument("--out", default="reports/latest")
    evaluate.add_argument("--fail-on-page", action="store_true")

    args = parser.parse_args()
    if args.command == "evaluate":
        config = load_config(args.config)
        report = evaluate_slos(config, load_metrics(args.metrics))
        write_report(report, args.out)
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return 2 if args.fail_on_page and report.decision.value == "page" else 0
    return 1
