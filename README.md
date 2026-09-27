# Secure Document RAG Agent

A dependency-light prototype for traceable document retrieval with explicit source references and a simple action gate.

## Implemented
- document/chunk ingestion
- token-overlap retrieval
- source/provenance retention
- sensitivity-aware access filtering
- answer context packets with citations
- minimum-evidence gate before downstream use
- tests for retrieval, access filtering and insufficient evidence

## Run
```bash
python -m unittest discover -s tests -v
python secure_doc_rag_agent.py
```

## Security boundary
This is not a production vector database or hardened enterprise RAG stack. It deliberately avoids external model/API calls so retrieval behavior remains inspectable. Encryption, authentication, semantic embeddings and adversarial prompt-injection testing are future work.
