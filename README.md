# Secure Document RAG Agent

> **Traceable retrieval with provenance, sensitivity filtering, evidence packets, and a minimum-evidence gate.**

Document assistants should not merely retrieve text; they should preserve where it came from, respect sensitivity boundaries, and expose when the retrieved evidence is too weak for downstream action.

## Implemented
- chunk ingestion with source/provenance metadata
- token-overlap retrieval
- sensitivity-aware access filtering
- deterministic top-k ranking
- traceable retrieval hits
- evidence packet generation
- minimum-hit sufficiency gate

## Repository structure
- `secure_doc_rag_agent.py` — core implementation
- `tests/` — deterministic tests
- `examples/` — synthetic example
- `docs/architecture.md` — design
- `docs/research-agenda.md` — experiments and paper lineage
- `STATUS.md` — claims boundary
- `CITATION.cff` — citation metadata

## Run
```bash
python -m unittest discover -s tests -v
python secure_doc_rag_agent.py
```

## Pipeline
**documents/chunks → access filter → query tokenization → retrieval scoring → ranked hits → evidence packet → sufficiency gate**

## Research lineage
This descends from the Document Processing & Knowledge Agent and EXIM document-intelligence work: ingestion → extraction → retrieval → validation → downstream action, with special attention to privacy and error propagation.

## Evaluation direction
Use synthetic document corpora with sensitivity labels, distractors, missing evidence, and conflicting sources. Compare traceable gated retrieval against ungated retrieval-only output.

## Maturity
**Research prototype.** This is not a production vector database, encryption system, enterprise access-control layer, or hardened prompt-injection defense. It currently uses transparent lexical overlap rather than embeddings.
