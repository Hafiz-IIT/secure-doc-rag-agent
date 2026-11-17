# Evaluation

## Research question
Can a small provenance-preserving retrieval layer improve traceability and reduce unsupported downstream actions in document agents?

## Metrics
- Retrieval precision
- Sensitive-data leakage rate
- Source traceability
- Insufficient-evidence detection
- Citation coverage
- Cross-tenant and cross-owner retrieval leakage

## Implemented access filter
- Chunks carry a tenant identifier and optional owner identifier.
- Retrieval filters by tenant and, when supplied, owner.
- Sensitivity labels are filtered through an explicit allowlist.
- Unicode-aware tokenization supports Bengali, Hindi and other scripts.

## Security limitations
Tenant and principal identifiers are parameters supplied by the caller; this in-memory prototype does not authenticate users or prove that those identifiers are trustworthy. A production service must derive them from authenticated, authorization-checked identity claims, enforce access control at the storage/query layer, and test concurrent isolation. Chunks are held in process memory and are not encrypted or persisted securely.

The retrieval score is token overlap, not semantic relevance or calibrated confidence. Evidence sufficiency is a count threshold, not proof that the retrieved sources entail an answer. Returned snippets are extractive and require human review before consequential use.

## Falsification criteria
- Private chunks appear without explicit access.
- Cross-tenant or cross-owner retrieval occurs.
- Returned content loses its source.
- Evidence sufficiency becomes true below the configured threshold.
- A caller-supplied identity value is mistaken for authenticated identity.
