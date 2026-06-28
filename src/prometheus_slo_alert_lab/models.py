from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    ok = "ok"
    ticket = "ticket"
    page = "page"


class WindowMetric(BaseModel):
    service: str
    slo: str
    window: str
    total_events: int = Field(ge=0)
    bad_events: int = Field(ge=0)

    @field_validator("bad_events")
    @classmethod
    def bad_events_cannot_exceed_total(cls, value: int, info) -> int:
        total = info.data.get("total_events")
        if total is not None and value > total:
            raise ValueError("bad_events cannot exceed total_events")
        return value


class AlertPolicy(BaseModel):
    name: str
    severity: Severity
    short_window: str
    long_window: str
    burn_rate_threshold: float = Field(gt=0)


class SloTarget(BaseModel):
    service: str
    slo: str
    objective: float = Field(gt=0, lt=100)

    @property
    def error_budget_ratio(self) -> float:
        return max(0.0, (100.0 - self.objective) / 100.0)


class SloConfig(BaseModel):
    targets: list[SloTarget]
    policies: list[AlertPolicy]


class WindowEvaluation(BaseModel):
    service: str
    slo: str
    window: str
    total_events: int
    bad_events: int
    error_rate: float
    burn_rate: float


class PolicyEvaluation(BaseModel):
    policy: str
    severity: Severity
    service: str
    slo: str
    short_window: str
    long_window: str
    threshold: float
    short_burn_rate: float
    long_burn_rate: float
    triggered: bool


class SloEvaluationReport(BaseModel):
    decision: Severity
    services_evaluated: int
    windows: list[WindowEvaluation]
    policies: list[PolicyEvaluation]
    recommendations: list[str]


class ScenarioStage(BaseModel):
    name: str
    minutes_from_start: int = Field(ge=0)
    metrics: list[dict]


class ScenarioStageEvaluation(BaseModel):
    name: str
    minutes_from_start: int
    decision: Severity
    triggered_policies: int
    max_burn_rate: float
    recommendations: list[str]


class ScenarioReport(BaseModel):
    decision: Severity
    stages: list[ScenarioStageEvaluation]
    recommendations: list[str]
