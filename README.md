# Secure Document RAG Agent

<p align="center"><strong>Evidence-Grounded Retrieval for Sensitive Documents</strong><br/><sub>Retrieve only what the evidence supports—and preserve where it came from.</sub></p>

<p align="center"><a href="https://github.com/Hafiz-IIT/secure-doc-rag-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hafiz-IIT/secure-doc-rag-agent/ci.yml?label=CI" alt="CI"/></a> <img src="https://img.shields.io/badge/status-reproducible%20prototype-blue" alt="Prototype"/></p>

## Research question

**How can a document agent remain useful without turning weak retrieval into confident unsupported answers?**

## Pipeline

```
Document chunks + metadata
        ↓
Sensitivity filter
        ↓
Lexical retrieval
        ↓
Ranked evidence
        ↓
Minimum-evidence gate
        ↓
Citation-preserving draft / NO ANSWER
```

## Try it

```bash
python secure_doc_rag_agent.py
python -m unittest discover -s tests -v
```

`grounded_response.py` adds a citation-preserving extractive response layer and deliberately returns no answer when the evidence threshold is not met.

## Implemented

- chunk ingestion
- source/provenance metadata
- sensitivity-aware filtering
- token-overlap retrieval
- ranked hits
- evidence packets
- minimum-evidence gate
- citation-preserving drafts
- deterministic tests + CI

## Boundary

This is a controlled retrieval prototype—not a production enterprise RAG platform and not a claim of secure handling of arbitrary confidential data.

Related: [Memory Governor](https://github.com/Hafiz-IIT/memory-governor) · [EXIM Document Truth Bench](https://github.com/Hafiz-IIT/exim-document-truth-bench)
