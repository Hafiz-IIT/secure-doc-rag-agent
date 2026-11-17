import unittest

from secure_doc_rag_agent import Chunk, SecureDocRAG


class SecureDocRAGTests(unittest.TestCase):
    def test_retrieval_preserves_source(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "invoice", "gross weight 1200 kg"))
        packet = rag.evidence_packet("gross weight")
        self.assertTrue(packet["sufficient_evidence"])
        self.assertEqual(packet["sources"][0]["source"], "invoice")

    def test_sensitive_chunk_filtered_by_default(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "private-note", "customer passport number", sensitivity="private"))
        self.assertEqual(rag.retrieve("passport number"), [])
        hits = rag.retrieve("passport number", allowed_sensitivities=("normal", "private"))
        self.assertEqual(len(hits), 1)

    def test_minimum_evidence_gate(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "one", "shipment delayed"))
        packet = rag.evidence_packet("shipment delayed", min_hits=2)
        self.assertFalse(packet["sufficient_evidence"])

    def test_tenant_isolation(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "tenant-a-doc", "gross weight 1200 kg", tenant_id="tenant-a"))
        rag.add(Chunk("b", "tenant-b-doc", "gross weight 900 kg", tenant_id="tenant-b"))
        hits = rag.retrieve("gross weight", tenant_id="tenant-a")
        self.assertEqual([hit.chunk.source for hit in hits], ["tenant-a-doc"])

    def test_owner_scoped_chunks_require_matching_principal(self):
        rag = SecureDocRAG()
        rag.add(Chunk("private", "owner-doc", "passport number", tenant_id="tenant-a", owner_id="user-a"))
        self.assertEqual(rag.retrieve("passport number", tenant_id="tenant-a"), [])
        self.assertEqual(
            len(rag.retrieve("passport number", tenant_id="tenant-a", principal_id="user-a")),
            1,
        )
        self.assertEqual(rag.retrieve("passport number", tenant_id="tenant-a", principal_id="user-b"), [])

    def test_duplicate_chunk_id_within_tenant_is_rejected(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "one", "first"))
        with self.assertRaises(ValueError):
            rag.add(Chunk("a", "two", "second"))

    def test_unicode_text_is_tokenized(self):
        rag = SecureDocRAG()
        rag.add(Chunk("bn", "bangla-doc", "মোট ওজন ১২০০ কেজি"))
        self.assertEqual(len(rag.retrieve("মোট ওজন")), 1)

    def test_invalid_retrieval_limits_are_rejected(self):
        rag = SecureDocRAG()
        with self.assertRaises(ValueError):
            rag.retrieve("query", top_k=0)
        with self.assertRaises(ValueError):
            rag.evidence_packet("query", min_hits=0)


if __name__ == "__main__":
    unittest.main()
