# prometheus-slo-alert-lab

Production-shaped SRE and platform engineering project for evaluating Prometheus-style
SLO burn rates, routing alerts by severity, and producing incident-ready reports.

## Business Problem

Fast-moving teams need a reliable way to decide whether an error-budget burn should page
on-call, open a ticket, or remain informational. This project turns windowed service
metrics into deterministic SLO decisions that can run locally, in CI, or behind an API.

## Architecture

```mermaid
flowchart LR
    A[Prometheus window metrics] --> B[SLO config]
    B --> C[Burn-rate evaluator]
    A --> C
    C --> D[CLI gate]
    C --> E[FastAPI /evaluate]
    C --> F[Markdown and JSON reports]
    E --> G[Prometheus /metrics]
    E --> H[Docker image]
    H --> I[Kubernetes manifests]
    H --> J[Terraform skeleton]
```

## What It Demonstrates

- Multi-window SLO burn-rate evaluation for incident response workflows
- Deterministic page/ticket/ok routing suitable for CI and production support
- FastAPI service with typed request and response schemas
- Prometheus metrics for evaluation count and latency
- Docker, Kubernetes, Terraform, tests, and CI-ready automation
- Recruiter-readable docs that explain tradeoffs and operational boundaries

## Local Setup

```bash
make setup
source .venv/bin/activate
```

## Run Tests

```bash
make test
make lint
```

## Evaluate Example Metrics

```bash
make evaluate
```

The sample checkout service breaches the fast page policy. The command writes:

- `reports/latest/slo_report.json`
- `reports/latest/slo_report.md`

For CI/CD gates, add `--fail-on-page` so page-worthy incidents exit with code `2`:

```bash
slo-alert-lab evaluate --config examples/slo_config.yaml --metrics examples/window_metrics.json --fail-on-page
```

## Run API Locally

```bash
make run
curl http://localhost:8000/health
```

Evaluate a payload:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d @docs/sample_api_payload.json
```

Prometheus metrics:

```bash
curl http://localhost:8000/metrics
```

## Docker Usage

```bash
make docker-build
docker run --rm -p 8000:8000 prometheus-slo-alert-lab:local
```

## Kubernetes Deployment

```bash
kubectl apply -k infra/k8s
kubectl rollout status deployment/prometheus-slo-alert-lab
kubectl port-forward service/prometheus-slo-alert-lab 8000:80
```

The manifests include readiness/liveness probes, resource requests/limits,
Prometheus scrape annotations, and a non-root security context.

## Terraform Notes

`infra/terraform` contains a small AWS ECS skeleton for a containerized API service.
It is intentionally parameterized and does not require cloud credentials for local use.

```bash
cd infra/terraform
terraform init
terraform plan
```

## CI/CD

This environment's GitHub token does not currently have `workflow` scope, so the
GitHub Actions workflow is stored at `docs/github-actions/ci.yml`. To publish it as
a real workflow later:

```bash
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
cp docs/github-actions/ci.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "Add CI workflow"
git push
```

## Observability and Security

- `/metrics` exposes Prometheus-compatible counters and latency histograms.
- Evaluation output avoids secrets and stores only aggregate SLO window metrics.
- Docker runs as a non-root user.
- Kubernetes security context drops Linux capabilities and disables privilege escalation.
- Config and metrics are loaded from explicit files or typed API payloads.

## Limitations

- This lab uses precomputed window metrics rather than querying a live Prometheus server.
- Alert policies are deterministic examples, not a replacement for service-specific review.
- Terraform is a deployment skeleton, not a complete production network stack.

## What This Project Proves

This repo demonstrates practical SRE, DevOps, and AI platform support skills: SLO
reasoning, incident routing, testable automation, API packaging, observability, and
deployment manifests that map to real production workflows without claiming fake
production usage.
