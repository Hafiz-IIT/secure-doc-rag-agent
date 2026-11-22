# Status

## Implemented
- chunk ingestion with non-empty metadata validation
- duplicate chunk-ID rejection within a tenant
- tenant-filtered retrieval
- explicit RetrievalAuthorization context for non-default tenant or sensitivity access
- default-deny behaviour for private/restricted sensitivity labels
- Unicode-aware lexical tokenization, including combining marks
- deterministic top-k ranking
- traceable retrieval hits and source-preserving evidence packets
- positive-integer validation for top_k, min_hits and max_snippets
- minimum-hit sufficiency gate
- tests + GitHub Actions CI

## Security boundary
RetrievalAuthorization is a data structure, not an authentication mechanism. The calling application must create it only after authenticating the principal and authorizing tenant/sensitivity access. This repository does not issue signed capabilities, verify identity, or enforce enterprise IAM.

## Not claimed
- semantic/vector retrieval quality or calibrated relevance thresholds
- authenticated authorization, enterprise IAM or signed capabilities
- field-level redaction or encryption at rest
- source authenticity or cryptographic provenance verification
- LLM answer correctness
- prompt-injection immunity
- production security

## Boundary
This remains a controlled retrieval prototype. It uses transparent lexical overlap rather than embeddings, returns source text without field-level redaction, and does not implement a production authorization service or hardened prompt-injection defense.
