.PHONY: setup test lint evaluate simulate history run docker-build

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check .

evaluate:
	PYTHONPATH=src .venv/bin/python -m prometheus_slo_alert_lab.cli evaluate --config examples/slo_config.yaml --metrics examples/window_metrics.json --out reports/latest

simulate:
	PYTHONPATH=src .venv/bin/python -m prometheus_slo_alert_lab.cli simulate --config examples/slo_config.yaml --scenario examples/incident_scenario.json --out reports/scenario

history:
	PYTHONPATH=src .venv/bin/python -m prometheus_slo_alert_lab.cli history --config examples/slo_config.yaml --history examples/deploy_history.json --out reports/history

run:
	PYTHONPATH=src .venv/bin/uvicorn prometheus_slo_alert_lab.api:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -f infra/docker/Dockerfile -t prometheus-slo-alert-lab:local .
