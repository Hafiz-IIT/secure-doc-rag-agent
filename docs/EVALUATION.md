# Evaluation

## Research question
Can a small provenance-preserving retrieval layer improve traceability and reduce unsupported downstream actions in document agents?

## Metrics
- Retrieval precision
- Sensitive-data leakage rate
- Source traceability
- Insufficient-evidence detection
- Citation coverage

## Falsification criteria
- Private chunks appear without explicit access.
- Returned content loses its source.
- Evidence sufficiency becomes true below the configured threshold.
