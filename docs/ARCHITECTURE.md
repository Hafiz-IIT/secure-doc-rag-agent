# Architecture

Document chunks + metadata → sensitivity filter → lexical retrieval → ranked hits → provenance-preserving evidence packet → minimum-evidence gate.

## Access-control boundary
Every chunk is bound to a tenant and owner, with explicit per-principal sharing. Retrieval requires the caller's tenant and principal and filters before ranking. This is an in-memory authorization boundary only; the prototype does not authenticate callers or cryptographically verify provenance labels.

## Invariants
1. Default retrieval must exclude disallowed sensitivity classes.
2. Every hit must preserve source and provenance.
3. Insufficient evidence must be visible to downstream callers.

## Integration rule
Future external adapters must not discard provenance, access-control decisions, uncertainty, or failure states.
