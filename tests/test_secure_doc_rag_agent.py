import unittest

from secure_doc_rag_agent import Chunk, RetrievalAuthorization, SecureDocRAG


class SecureDocRAGTests(unittest.TestCase):
    def test_retrieval_preserves_source(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "invoice", "gross weight 1200 kg"))
        packet = rag.evidence_packet("gross weight")
        self.assertTrue(packet["sufficient_evidence"])
        self.assertEqual(packet["sources"][0]["source"], "invoice")

    def test_sensitive_chunk_filtered_by_default_and_authorized_explicitly(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "private-note", "customer passport number", sensitivity="private"))
        self.assertEqual(rag.retrieve("passport number"), [])
        auth = RetrievalAuthorization(
            principal_id="reviewer-1",
            tenant_id="default",
            allowed_sensitivities=("normal", "private"),
        )
        self.assertEqual(len(rag.retrieve("passport number", authorization=auth)), 1)

    def test_tenant_isolation(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "tenant-a-doc", "shipment delayed", tenant_id="tenant-a"))
        rag.add(Chunk("a", "tenant-b-doc", "shipment delayed", tenant_id="tenant-b"))
        auth_a = RetrievalAuthorization("principal-a", "tenant-a")
        hits = rag.retrieve("shipment delayed", authorization=auth_a)
        self.assertEqual([hit.chunk.source for hit in hits], ["tenant-a-doc"])

    def test_duplicate_chunk_ids_within_tenant_are_rejected(self):
        rag = SecureDocRAG()
        rag.add(Chunk("same", "one", "shipment delayed"))
        with self.assertRaisesRegex(ValueError, "duplicate chunk_id"):
            rag.add(Chunk("same", "two", "shipment delayed"))

    def test_same_chunk_id_in_different_tenants_is_allowed(self):
        rag = SecureDocRAG()
        rag.add(Chunk("same", "tenant-a", "shipment delayed", tenant_id="tenant-a"))
        rag.add(Chunk("same", "tenant-b", "shipment delayed", tenant_id="tenant-b"))
        self.assertEqual(len(rag.retrieve("shipment delayed")), 0)
        self.assertEqual(
            len(rag.retrieve("shipment delayed", authorization=RetrievalAuthorization("a", "tenant-a"))),
            1,
        )

    def test_minimum_evidence_gate(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "one", "shipment delayed"))
        packet = rag.evidence_packet("shipment delayed", min_hits=2)
        self.assertFalse(packet["sufficient_evidence"])

    def test_invalid_query_and_numeric_limits_are_rejected(self):
        rag = SecureDocRAG()
        for query in ("", "   "):
            with self.assertRaisesRegex(ValueError, "query"):
                rag.retrieve(query)
        for top_k in (0, -1, True, 1.5):
            with self.subTest(top_k=top_k), self.assertRaisesRegex(ValueError, "top_k"):
                rag.retrieve("shipment", top_k=top_k)
        for min_hits in (0, -1, True):
            with self.subTest(min_hits=min_hits), self.assertRaisesRegex(ValueError, "min_hits"):
                rag.evidence_packet("shipment", min_hits=min_hits)

    def test_invalid_chunk_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "chunk_id"):
            Chunk("", "invoice", "gross weight")
        with self.assertRaisesRegex(ValueError, "tenant_id"):
            Chunk("a", "invoice", "gross weight", tenant_id=" ")

    def test_unicode_tokenization_supports_non_latin_scripts(self):
        self.assertIn("বাংলা", __import__("secure_doc_rag_agent").tokens("বাংলা নথি"))
        self.assertIn("हिंदी", __import__("secure_doc_rag_agent").tokens("हिंदी दस्तावेज़"))

    def test_empty_authorized_sensitivity_set_returns_no_hits(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "invoice", "gross weight"))
        auth = RetrievalAuthorization("principal", "default", allowed_sensitivities=())
        self.assertEqual(rag.retrieve("gross weight", authorization=auth), [])


if __name__ == "__main__":
    unittest.main()
