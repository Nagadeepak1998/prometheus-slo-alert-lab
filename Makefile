.PHONY: setup test lint evaluate run docker-build

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

evaluate:
	slo-alert-lab evaluate --config examples/slo_config.yaml --metrics examples/window_metrics.json --out reports/latest

run:
	uvicorn prometheus_slo_alert_lab.api:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -f infra/docker/Dockerfile -t prometheus-slo-alert-lab:local .
