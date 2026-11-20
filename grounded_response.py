from __future__ import annotations

from dataclasses import dataclass

from secure_doc_rag_agent import SecureDocRAG


@dataclass(frozen=True)
class GroundedDraft:
    answer: str | None
    citations: tuple[str, ...]
    sufficient_evidence: bool


def extractive_draft(
    rag: SecureDocRAG,
    query: str,
    *,
    tenant_id: str,
    principal_id: str,
    min_hits: int = 1,
    allowed_sensitivities: tuple[str, ...] = ("normal",),
    max_snippets: int = 3,
) -> GroundedDraft:
    if isinstance(min_hits, bool) or not isinstance(min_hits, int) or min_hits < 1:
        raise ValueError("min_hits must be a positive integer")
    if isinstance(max_snippets, bool) or not isinstance(max_snippets, int) or max_snippets < 1:
        raise ValueError("max_snippets must be a positive integer")
    if max_snippets < min_hits:
        raise ValueError("max_snippets must be at least min_hits so the answer retains the required evidence")
    packet = rag.evidence_packet(
        query,
        tenant_id=tenant_id,
        principal_id=principal_id,
        min_hits=min_hits,
        allowed_sensitivities=allowed_sensitivities,
        top_k=max(max_snippets, min_hits),
    )
    if not packet["sufficient_evidence"]:
        return GroundedDraft(None, (), False)

    sources = packet["sources"][:max_snippets]
    citations = tuple(f'{source["source"]}#{source["chunk_id"]}' for source in sources)
    answer = " ".join(source["text"].strip() for source in sources)
    return GroundedDraft(answer, citations, True)
