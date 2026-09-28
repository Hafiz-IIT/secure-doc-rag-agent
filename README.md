# Secure Document RAG Agent

> Traceable document-retrieval prototype with provenance-preserving chunks, sensitivity filters and an explicit evidence gate.

## Status
**Reproducible prototype** with executable Python, tests, and GitHub Actions CI.

## Problem
Document agents can retrieve sensitive or weakly supported content and then pass it downstream without preserving source provenance or acknowledging insufficient evidence.

## Architecture
Document chunks + metadata → sensitivity filter → lexical retrieval → ranked hits → provenance-preserving evidence packet → minimum-evidence gate.

## Quick start
```bash
python -m unittest discover -s tests -v
python secure_doc_rag_agent.py
```

## Implemented
- Chunk ingestion
- Source/provenance metadata
- Sensitivity-aware filtering
- Token-overlap retrieval
- Ranked hits
- Evidence packet construction
- Minimum-evidence gate
- Tests and CI

## Research lineage
- *Privacy-Preserving Architectures for Intelligent Consumer Applications*
- *The Future of Digital Trust: Secure Data Interactions in User-Centric Platforms*
- *Human–AI Symbiosis: Toward Next-Generation Consumer Applications*

## Evaluation
The current deterministic tests target traceability, sensitive-chunk exclusion and minimum-evidence behavior.

## Limitations
- Lexical retrieval only
- No production authentication
- No encryption-at-rest layer
- No LLM generation bundled
- No claim of prompt-injection robustness yet

## License
MIT.

## Extended implementation

- `grounded_response.py` — extractive evidence drafts that preserve source/chunk citations and return no answer when the evidence threshold is not met.
- `tests/test_grounded_response.py` — citation and insufficient-evidence tests.
