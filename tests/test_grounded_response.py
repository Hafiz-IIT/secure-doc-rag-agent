import unittest

from grounded_response import extractive_draft
from secure_doc_rag_agent import Chunk, SecureDocRAG


class GroundedResponseTests(unittest.TestCase):
    def test_draft_preserves_citations(self):
        rag = SecureDocRAG()
        rag.add(Chunk("c1", "invoice-1", "Gross weight is 1200 kg.", "tenant-a", "user-a"))
        draft = extractive_draft(rag, "gross weight", tenant_id="tenant-a", principal_id="user-a")
        self.assertTrue(draft.sufficient_evidence)
        self.assertEqual(draft.citations, ("invoice-1#c1",))
        self.assertIn("1200", draft.answer)

    def test_insufficient_evidence_returns_no_answer(self):
        rag = SecureDocRAG()
        rag.add(Chunk("c1", "one", "shipment delayed", "tenant-a", "user-a"))
        draft = extractive_draft(rag, "shipment delayed", tenant_id="tenant-a",
                                 principal_id="user-a", min_hits=2)
        self.assertFalse(draft.sufficient_evidence)
        self.assertIsNone(draft.answer)

    def test_invalid_snippet_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            extractive_draft(SecureDocRAG(), "x", tenant_id="tenant-a",
                             principal_id="user-a", max_snippets=0)


if __name__ == "__main__":
    unittest.main()
