# Case Study: Prometheus SLO Alert Lab

## Problem

SRE teams need to separate normal noise from true error-budget emergencies. A raw
Prometheus alert can say that errors increased, but engineers still need a repeatable
decision: page immediately, open a ticket, or keep watching.

## Approach

This project models a small SLO alerting control plane. It accepts service objectives
and windowed good/bad event counts, computes burn rates, evaluates multi-window alert
policies, and emits a recruiter-readable incident report.

## Design Choices

- **Pydantic models** keep API and CLI validation consistent.
- **Shared evaluator** prevents drift between command-line and service behavior.
- **Multi-window burn policies** reduce noisy alerts compared with one-window checks.
- **Prometheus metrics** make the evaluator observable when deployed as a service.
- **Kubernetes and Terraform skeletons** show where the service would run in a platform
  environment without requiring cloud credentials for the demo.

## Operational Flow

1. Prometheus recording rules or exports provide windowed good/bad event counts.
2. The evaluator calculates error rate and burn rate against each SLO objective.
3. Page policies require both short and long windows to exceed the configured threshold.
4. The CLI exits non-zero for severe incidents; the API returns a typed report.
5. Operators use the Markdown report as an incident handoff artifact.

## Tradeoffs

- The lab does not query Prometheus directly, which keeps it deterministic for tests and
  portfolio review.
- Policy thresholds are examples. Real services should tune them using incident history
  and user-impact tolerance.
- The API has no authentication because the focus is SLO evaluation and deployment shape.
  A real internal service should sit behind platform auth and network controls.

## Production-Readiness Checklist

- [x] Typed SLO config and metric payloads
- [x] CLI and API entrypoints
- [x] Multi-window page and ticket policies
- [x] JSON and Markdown reports
- [x] Prometheus-compatible service metrics
- [x] Unit and API tests
- [x] Dockerfile
- [x] Kubernetes manifests
- [x] Terraform deployment skeleton
- [x] CI workflow stored under docs for workflow-scope-safe publishing
- [ ] Live Prometheus query integration
- [ ] Alertmanager webhook integration
- [ ] Grafana dashboard JSON
- [ ] Platform authentication and audit logs

## Next Improvements

1. Add a Prometheus HTTP client mode that reads configured PromQL queries.
2. Generate Alertmanager route snippets from the same policy config.
3. Add a Grafana dashboard for burn-rate trend review.
4. Store evaluation history for post-incident review.
5. Add OpenTelemetry traces around API evaluation calls.
