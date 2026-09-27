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


if __name__ == "__main__":
    unittest.main()
