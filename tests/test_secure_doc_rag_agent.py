import unittest

from secure_doc_rag_agent import Chunk, SecureDocRAG


class SecureDocRAGTests(unittest.TestCase):
    def setUp(self):
        self.tenant = "tenant-a"
        self.owner = "user-a"

    def test_retrieval_preserves_source(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "invoice", "gross weight 1200 kg", self.tenant, self.owner))
        packet = rag.evidence_packet("gross weight", tenant_id=self.tenant, principal_id=self.owner)
        self.assertTrue(packet["sufficient_evidence"])
        self.assertEqual(packet["sources"][0]["source"], "invoice")

    def test_sensitive_chunk_filtered_by_default(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "private-note", "customer passport number", self.tenant, self.owner,
                      sensitivity="private"))
        self.assertEqual(rag.retrieve("passport number", tenant_id=self.tenant,
                                      principal_id=self.owner), [])
        hits = rag.retrieve("passport number", tenant_id=self.tenant, principal_id=self.owner,
                            allowed_sensitivities=("normal", "private"))
        self.assertEqual(len(hits), 1)

    def test_invalid_allowed_readers_and_query_rejected(self):
        with self.assertRaises(ValueError):
            Chunk("x", "doc", "text", self.tenant, self.owner, allowed_readers=(" ",))
        rag = SecureDocRAG()
        with self.assertRaises(ValueError):
            rag.retrieve(None, tenant_id=self.tenant, principal_id=self.owner)

    def test_invalid_sensitivity_filter_rejected(self):
        rag = SecureDocRAG()
        with self.assertRaises(ValueError):
            rag.retrieve("weight", tenant_id=self.tenant, principal_id=self.owner,
                         allowed_sensitivities=())

    def test_duplicate_chunk_id_within_tenant_is_rejected(self):
        rag = SecureDocRAG()
        rag.add(Chunk("same", "invoice-a", "weight 1200", self.tenant, self.owner))
        with self.assertRaises(ValueError):
            rag.add(Chunk("same", "invoice-b", "weight 1300", self.tenant, self.owner))

    def test_minimum_evidence_gate(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "one", "shipment delayed", self.tenant, self.owner))
        packet = rag.evidence_packet("shipment delayed", tenant_id=self.tenant,
                                     principal_id=self.owner, min_hits=2)
        self.assertFalse(packet["sufficient_evidence"])

    def test_tenant_and_owner_isolation(self):
        rag = SecureDocRAG()
        rag.add(Chunk("a", "tenant-a-doc", "shipment weight 1200", "tenant-a", "user-a"))
        rag.add(Chunk("b", "tenant-b-doc", "shipment weight 1300", "tenant-b", "user-a"))
        rag.add(Chunk("c", "other-user-doc", "shipment weight 1400", "tenant-a", "user-b"))
        rag.add(Chunk("d", "shared-doc", "shipment weight 1500", "tenant-a", "user-b",
                      allowed_readers=("user-a",)))
        hits = rag.retrieve("shipment weight", tenant_id="tenant-a", principal_id="user-a")
        self.assertEqual({h.chunk.chunk_id for h in hits}, {"a", "d"})

    def test_minimum_hit_count_can_exceed_default_top_k(self):
        rag = SecureDocRAG()
        for i in range(4):
            rag.add(Chunk(str(i), f"source-{i}", "shared shipment fact",
                          self.tenant, self.owner))
        packet = rag.evidence_packet("shipment fact", tenant_id=self.tenant,
                                     principal_id=self.owner, min_hits=4)
        self.assertTrue(packet["sufficient_evidence"])
        self.assertEqual(len(packet["sources"]), 4)

    def test_bengali_and_devanagari_tokens_are_supported(self):
        self.assertIn("ওজন", __import__("secure_doc_rag_agent").tokens("মোট ওজন ১২০০ কেজি"))
        self.assertIn("वजन", __import__("secure_doc_rag_agent").tokens("कुल वजन १२०० किलोग्राम"))

    def test_invalid_gate_parameters_are_rejected(self):
        rag = SecureDocRAG()
        with self.assertRaises(ValueError):
            rag.retrieve("x", tenant_id=self.tenant, principal_id=self.owner, top_k=0)
        with self.assertRaises(ValueError):
            rag.evidence_packet("x", tenant_id=self.tenant, principal_id=self.owner, min_hits=0)


if __name__ == "__main__":
    unittest.main()
