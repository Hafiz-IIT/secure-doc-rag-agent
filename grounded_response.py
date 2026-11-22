from __future__ import annotations

from dataclasses import dataclass

from secure_doc_rag_agent import RetrievalAuthorization, SecureDocRAG


@dataclass(frozen=True)
class GroundedDraft:
    answer: str | None
    citations: tuple[str, ...]
    sufficient_evidence: bool


def extractive_draft(
    rag: SecureDocRAG,
    query: str,
    *,
    min_hits: int = 1,
    authorization: RetrievalAuthorization | None = None,
    max_snippets: int = 3,
) -> GroundedDraft:
    if isinstance(max_snippets, bool) or not isinstance(max_snippets, int) or max_snippets <= 0:
        raise ValueError("max_snippets must be a positive integer")
    packet = rag.evidence_packet(
        query,
        min_hits=min_hits,
        authorization=authorization,
        top_k=max_snippets,
    )
    if not packet["sufficient_evidence"]:
        return GroundedDraft(None, (), False)

    sources = packet["sources"]
    citations = tuple(
        f'{source["source"]}#{source["chunk_id"]}'
        for source in sources
    )
    answer = " ".join(source["text"].strip() for source in sources)
    return GroundedDraft(answer, citations, True)
