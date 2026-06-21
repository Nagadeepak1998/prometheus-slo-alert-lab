from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from starlette.responses import Response

from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.models import SloConfig, SloEvaluationReport

app = FastAPI(title="Prometheus SLO Alert Lab", version="0.1.0")

evaluations_total = Counter(
    "slo_alert_lab_evaluations_total",
    "Total SLO evaluations by final decision.",
    ["decision"],
)
evaluation_latency = Histogram(
    "slo_alert_lab_evaluation_seconds",
    "SLO evaluation latency in seconds.",
)


class EvaluationRequest(BaseModel):
    config: SloConfig
    metrics: list[dict]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=SloEvaluationReport)
def evaluate(request: EvaluationRequest) -> SloEvaluationReport:
    with evaluation_latency.time():
        report = evaluate_slos(request.config, request.metrics)
    evaluations_total.labels(decision=report.decision.value).inc()
    return report


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
