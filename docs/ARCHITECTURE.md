# Architecture

Document chunks + metadata → sensitivity filter → lexical retrieval → ranked hits → provenance-preserving evidence packet → minimum-evidence gate.

## Invariants
1. Default retrieval must exclude disallowed sensitivity classes.
2. Every hit must preserve source and provenance.
3. Insufficient evidence must be visible to downstream callers.

## Integration rule
Future external adapters must not discard provenance, access-control decisions, uncertainty, or failure states.
