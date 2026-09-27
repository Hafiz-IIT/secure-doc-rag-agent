from __future__ import annotations

from dataclasses import dataclass
import re


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: str
    text: str
    sensitivity: str = "normal"
    provenance: str = "uploaded-document"


@dataclass(frozen=True)
class RetrievalHit:
    chunk: Chunk
    score: float


class SecureDocRAG:
    def __init__(self):
        self._chunks: list[Chunk] = []

    def add(self, chunk: Chunk) -> None:
        self._chunks.append(chunk)

    def retrieve(
        self,
        query: str,
        *,
        allowed_sensitivities: tuple[str, ...] = ("normal",),
        top_k: int = 3,
    ) -> list[RetrievalHit]:
        q = tokens(query)
        hits: list[RetrievalHit] = []
        for chunk in self._chunks:
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
    ) -> dict:
        hits = self.retrieve(query, allowed_sensitivities=allowed_sensitivities)
        return {
            "query": query,
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
