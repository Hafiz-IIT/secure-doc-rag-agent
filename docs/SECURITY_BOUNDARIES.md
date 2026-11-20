# Security and retrieval boundaries

- Retrieval requires a tenant ID and principal ID and filters chunks by tenant plus owner/allowed-reader identity.
- The tenant/principal values are supplied to this library by its caller. They are not authenticated here. A production API must derive them from a verified session/token and must not trust arbitrary request-body values.
- Chunk IDs are unique within a tenant. The same ID may exist in a different tenant.
- Sensitivity labels are allowlisted by the caller; this prototype does not enforce an external classification authority.
- Search uses Unicode-normalized token overlap, not embeddings, semantic retrieval, BM25, or a calibrated relevance score.
- Evidence packets include source text. Do not expose them to users who are not authorized for every returned chunk.
- This is an in-memory demonstration, not a persistent encrypted multi-tenant document store. It has no authenticated uploader, audit log, key management, deletion propagation or production isolation certification.
