from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from starlette.responses import Response

from prometheus_slo_alert_lab.evaluator import evaluate_slos
from prometheus_slo_alert_lab.history import review_slo_history
from prometheus_slo_alert_lab.models import (
    HistoryReviewReport,
    ScenarioReport,
    SloConfig,
    SloEvaluationReport,
)
from prometheus_slo_alert_lab.scenario import simulate_scenario

app = FastAPI(title="Prometheus SLO Alert Lab", version="0.1.0")

evaluations_total = Counter(
    "slo_alert_lab_evaluations_total",
    "Total SLO evaluations by final decision.",
    ["decision"],
)
scenario_evaluations_total = Counter(
    "slo_alert_lab_scenario_evaluations_total",
    "Total incident scenario simulations by final decision.",
    ["decision"],
)
history_reviews_total = Counter(
    "slo_alert_lab_history_reviews_total",
    "Total SLO history reviews by final decision.",
    ["decision"],
)
evaluation_latency = Histogram(
    "slo_alert_lab_evaluation_seconds",
    "SLO evaluation latency in seconds.",
)


class EvaluationRequest(BaseModel):
    config: SloConfig
    metrics: list[dict]


class ScenarioRequest(BaseModel):
    config: SloConfig
    stages: list[dict]


class HistoryRequest(BaseModel):
    config: SloConfig
    windows: list[dict]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=SloEvaluationReport)
def evaluate(request: EvaluationRequest) -> SloEvaluationReport:
    with evaluation_latency.time():
        report = evaluate_slos(request.config, request.metrics)
    evaluations_total.labels(decision=report.decision.value).inc()
    return report


@app.post("/simulate", response_model=ScenarioReport)
def simulate(request: ScenarioRequest) -> ScenarioReport:
    with evaluation_latency.time():
        report = simulate_scenario(request.config, request.stages)
    scenario_evaluations_total.labels(decision=report.decision.value).inc()
    return report


@app.post("/history", response_model=HistoryReviewReport)
def history(request: HistoryRequest) -> HistoryReviewReport:
    with evaluation_latency.time():
        report = review_slo_history(request.config, request.windows)
    history_reviews_total.labels(decision=report.decision.value).inc()
    return report


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
