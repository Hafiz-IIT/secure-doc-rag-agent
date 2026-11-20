from __future__ import annotations

from dataclasses import dataclass, field
import unicodedata


def tokens(text: str) -> set[str]:
    """Unicode-aware NFKC/casefold tokenizer retaining letters, marks and numbers."""
    if not isinstance(text, str):
        raise ValueError("query/document text must be a string")
    normalized = unicodedata.normalize("NFKC", text).casefold()
    found: set[str] = set()
    current: list[str] = []
    for char in normalized:
        category = unicodedata.category(char)
        if category[0] in {"L", "M", "N"} or char == "_":
            current.append(char)
        elif current:
            found.add("".join(current))
            current = []
    if current:
        found.add("".join(current))
    return found


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    text: str
    tenant_id: str
    owner_id: str
    sensitivity: str = "normal"
    provenance: str = "uploaded-document"
    allowed_readers: tuple[str, ...] = ()

    def __post_init__(self):
        for name, value in (("chunk_id", self.chunk_id), ("source", self.source),
                            ("text", self.text), ("tenant_id", self.tenant_id),
                            ("owner_id", self.owner_id), ("sensitivity", self.sensitivity),
                            ("provenance", self.provenance)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.allowed_readers, tuple) or any(
            not isinstance(reader, str) or not reader.strip() for reader in self.allowed_readers
        ):
            raise ValueError("allowed_readers must be a tuple of non-empty identities")
        if len(set(self.allowed_readers)) != len(self.allowed_readers):
            raise ValueError("allowed_readers must be unique")


@dataclass(frozen=True)
class RetrievalHit:
    chunk: Chunk
    score: float


class SecureDocRAG:
    def __init__(self):
        self._chunks: list[Chunk] = []

    def add(self, chunk: Chunk) -> None:
        if not isinstance(chunk, Chunk):
            raise TypeError("chunk must be a Chunk")
        for name, value in (("chunk_id", chunk.chunk_id), ("source", chunk.source),
                            ("text", chunk.text), ("tenant_id", chunk.tenant_id),
                            ("owner_id", chunk.owner_id), ("sensitivity", chunk.sensitivity),
                            ("provenance", chunk.provenance)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if any(c.tenant_id == chunk.tenant_id and c.chunk_id == chunk.chunk_id for c in self._chunks):
            raise ValueError("chunk_id must be unique within a tenant")
        self._chunks.append(chunk)

    def retrieve(
        self,
        query: str,
        *,
        tenant_id: str,
        principal_id: str,
        allowed_sensitivities: tuple[str, ...] = ("normal",),
        top_k: int = 3,
    ) -> list[RetrievalHit]:
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id is required")
        if not isinstance(principal_id, str) or not principal_id.strip():
            raise ValueError("principal_id is required")
        if not isinstance(allowed_sensitivities, (tuple, list)) or not allowed_sensitivities or any(
            not isinstance(value, str) or not value.strip() for value in allowed_sensitivities
        ):
            raise ValueError("allowed_sensitivities must be a non-empty sequence of labels")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        q = tokens(query)
        if not q:
            return []
        hits: list[RetrievalHit] = []
        for chunk in self._chunks:
            if chunk.tenant_id != tenant_id:
                continue
            if chunk.owner_id != principal_id and principal_id not in chunk.allowed_readers:
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
        tenant_id: str,
        principal_id: str,
        min_hits: int = 1,
        allowed_sensitivities: tuple[str, ...] = ("normal",),
        top_k: int = 3,
    ) -> dict:
        if isinstance(min_hits, bool) or not isinstance(min_hits, int) or min_hits < 1:
            raise ValueError("min_hits must be a positive integer")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        # Retrieve enough candidates to make min_hits attainable.
        hits = self.retrieve(
            query, tenant_id=tenant_id, principal_id=principal_id,
            allowed_sensitivities=allowed_sensitivities,
            top_k=max(top_k, min_hits),
        )
        return {
            "query": query,
            "tenant_id": tenant_id,
            "principal_id": principal_id,
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
    rag.add(Chunk("1", "invoice-001", "Gross weight is 1200 kg and consignee is ACME.",
                  tenant_id="demo-tenant", owner_id="demo-user"))
    print(rag.evidence_packet("What is the gross weight?", tenant_id="demo-tenant",
                              principal_id="demo-user"))
