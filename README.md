# Team B — Checkout & Order Fulfillment Service (`team-b-checkout`)

Example application repository demonstrating how a second application team ("Team B") consumes the centralized **CodeMender Enterprise Reusable Workflows** (`Cotomacio/codemender-enterprise-workflows`) and streams FinOps token telemetry into the shared Google Cloud Storage & BigQuery FinOps analytics lake (`gs://codemender-latam-codemender-telemetry`).

## Workflows Inherited
- `.github/workflows/codemender-monthly-async.yml` -> Calls `Cotomacio/codemender-enterprise-workflows/.github/workflows/codemender-reusable.yml@main` (`deep` / `quick` scan + SARIF upload + GCS/BigQuery FinOps telemetry + Automated Fix PR).
- `.github/workflows/codemender-pr-gate.yml` -> Calls `Cotomacio/codemender-enterprise-workflows/.github/workflows/codemender-reusable.yml@main` (`diff` mode on Pull Requests).
