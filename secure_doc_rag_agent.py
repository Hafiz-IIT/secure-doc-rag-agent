from __future__ import annotations

from dataclasses import dataclass
import re


def tokens(text: str) -> set[str]:
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    # Unicode-aware tokenization keeps Bengali, Hindi and other scripts searchable.
    return set(re.findall(r"\w+", text.casefold(), flags=re.UNICODE))


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    text: str
    sensitivity: str = "normal"
    provenance: str = "uploaded-document"
    tenant_id: str = "default"
    owner_id: str | None = None


@dataclass(frozen=True)
class RetrievalHit:
    chunk: Chunk
    score: float


class SecureDocRAG:
    def __init__(self):
        self._chunks: list[Chunk] = []

    def add(self, chunk: Chunk) -> None:
        if any(not isinstance(value, str) or not value.strip()
               for value in (chunk.chunk_id, chunk.source, chunk.text, chunk.sensitivity,
                             chunk.provenance, chunk.tenant_id)):
            raise ValueError("chunk identifiers, source, text, sensitivity, provenance and tenant are required")
        if chunk.owner_id is not None and (not isinstance(chunk.owner_id, str) or not chunk.owner_id.strip()):
            raise ValueError("owner_id must be a non-empty string when supplied")
        if any(existing.tenant_id == chunk.tenant_id and existing.chunk_id == chunk.chunk_id
               for existing in self._chunks):
            raise ValueError("chunk_id must be unique within a tenant")
        self._chunks.append(chunk)

    def retrieve(
        self,
        query: str,
        *,
        allowed_sensitivities: tuple[str, ...] = ("normal",),
        top_k: int = 3,
        tenant_id: str = "default",
        principal_id: str | None = None,
    ) -> list[RetrievalHit]:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id is required")
        if principal_id is not None and (not isinstance(principal_id, str) or not principal_id.strip()):
            raise ValueError("principal_id must be non-empty when supplied")
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if isinstance(allowed_sensitivities, str) or not allowed_sensitivities or any(
            not isinstance(value, str) or not value.strip()
            for value in allowed_sensitivities
        ):
            raise ValueError("allowed_sensitivities must be a non-empty iterable of labels, not a string")
        q = tokens(query)
        hits: list[RetrievalHit] = []
        for chunk in self._chunks:
            if chunk.tenant_id != tenant_id:
                continue
            if chunk.owner_id is not None and chunk.owner_id != principal_id:
                continue
            if chunk.sensitivity not in allowed_sensitivities:
                continue
            c = tokens(chunk.text)
            overlap = len(q & c)
            if overlap == 0:
                continue
            score = overlap / max(1, len(q))
            hits.append(RetrievalHit(chunk, score))
        return sorted(hits, key=lambda h: (-h.score, h.chunk.chunk_id))[:top_k]

    def evidence_packet(
        self,
        query: str,
        *,
        min_hits: int = 1,
        allowed_sensitivities: tuple[str, ...] = ("normal",),
        tenant_id: str = "default",
        principal_id: str | None = None,
    ) -> dict:
        if not isinstance(min_hits, int) or isinstance(min_hits, bool) or min_hits < 1:
            raise ValueError("min_hits must be a positive integer")
        hits = self.retrieve(
            query, allowed_sensitivities=allowed_sensitivities,
            tenant_id=tenant_id, principal_id=principal_id,
        )
        return {
            "query": query,
            "tenant_id": tenant_id,
            "sufficient_evidence": len(hits) >= min_hits,
            "sources": [
                {
                    "chunk_id": h.chunk.chunk_id,
                    "source": h.chunk.source,
                    "provenance": h.chunk.provenance,
                    "score": round(h.score, 4),
                    "text": h.chunk.text,
                }
                for h in hits
            ],
        }


if __name__ == "__main__":
    rag = SecureDocRAG()
    rag.add(Chunk("1", "invoice-001", "Gross weight is 1200 kg and consignee is ACME."))
    print(rag.evidence_packet("What is the gross weight?"))
