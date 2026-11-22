from __future__ import annotations

from dataclasses import dataclass
import re


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def tokens(text: str) -> set[str]:
    _require_text(text, "text")
    return set(re.findall(r"\w+", text.casefold(), flags=re.UNICODE))


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    text: str
    sensitivity: str = "normal"
    provenance: str = "uploaded-document"
    tenant_id: str = "default"

    def __post_init__(self):
        for field in ("chunk_id", "source", "text", "sensitivity", "provenance", "tenant_id"):
            _require_text(getattr(self, field), field)


@dataclass(frozen=True)
class RetrievalAuthorization:
    """Authorization context that must be created by a trusted application layer.

    This prototype validates the shape of the context but does not authenticate
    the principal or issue signed capabilities.
    """
    principal_id: str
    tenant_id: str
    allowed_sensitivities: tuple[str, ...] = ("normal",)

    def __post_init__(self):
        _require_text(self.principal_id, "principal_id")
        _require_text(self.tenant_id, "tenant_id")
        if not isinstance(self.allowed_sensitivities, tuple):
            raise ValueError("allowed_sensitivities must be a tuple")
        if any(not isinstance(value, str) or not value.strip() for value in self.allowed_sensitivities):
            raise ValueError("allowed_sensitivities must contain non-empty strings")


@dataclass(frozen=True)
class RetrievalHit:
    chunk: Chunk
    score: float


class SecureDocRAG:
    def __init__(self):
        self._chunks: list[Chunk] = []

    def add(self, chunk: Chunk) -> None:
        if not isinstance(chunk, Chunk):
            raise TypeError("chunk must be a Chunk instance")
        if any(existing.chunk_id == chunk.chunk_id and existing.tenant_id == chunk.tenant_id for existing in self._chunks):
            raise ValueError(f"duplicate chunk_id within tenant: {chunk.chunk_id}")
        self._chunks.append(chunk)

    @staticmethod
    def _validate_positive_int(value: int, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field} must be a positive integer")

    def retrieve(
        self,
        query: str,
        *,
        authorization: RetrievalAuthorization | None = None,
        top_k: int = 3,
    ) -> list[RetrievalHit]:
        _require_text(query, "query")
        self._validate_positive_int(top_k, "top_k")
        if authorization is None:
            tenant_id = "default"
            allowed_sensitivities = ("normal",)
        else:
            if not isinstance(authorization, RetrievalAuthorization):
                raise TypeError("authorization must be a RetrievalAuthorization")
            tenant_id = authorization.tenant_id
            allowed_sensitivities = authorization.allowed_sensitivities
        if not allowed_sensitivities:
            return []

        q = tokens(query)
        hits: list[RetrievalHit] = []
        for chunk in self._chunks:
            if chunk.tenant_id != tenant_id or chunk.sensitivity not in allowed_sensitivities:
                continue
            c = tokens(chunk.text)
            overlap = len(q & c)
            if overlap == 0:
                continue
            score = overlap / max(1, len(q))
            hits.append(RetrievalHit(chunk, score))
        return sorted(hits, key=lambda hit: (-hit.score, hit.chunk.chunk_id))[:top_k]

    def evidence_packet(
        self,
        query: str,
        *,
        min_hits: int = 1,
        authorization: RetrievalAuthorization | None = None,
        top_k: int = 3,
    ) -> dict:
        self._validate_positive_int(min_hits, "min_hits")
        hits = self.retrieve(query, authorization=authorization, top_k=top_k)
        return {
            "query": query,
            "sufficient_evidence": len(hits) >= min_hits,
            "sources": [
                {
                    "chunk_id": hit.chunk.chunk_id,
                    "source": hit.chunk.source,
                    "provenance": hit.chunk.provenance,
                    "tenant_id": hit.chunk.tenant_id,
                    "score": round(hit.score, 4),
                    "text": hit.chunk.text,
                }
                for hit in hits
            ],
        }


if __name__ == "__main__":
    rag = SecureDocRAG()
    rag.add(Chunk("1", "invoice-001", "Gross weight is 1200 kg and consignee is ACME."))
    print(rag.evidence_packet("What is the gross weight?"))
