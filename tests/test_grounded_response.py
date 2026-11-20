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

    def test_snippet_cap_cannot_undercut_minimum_evidence_gate(self):
        rag = SecureDocRAG()
        for index in range(4):
            rag.add(Chunk(str(index), f"source-{index}", "shared evidence", "tenant-a", "user-a"))
        with self.assertRaisesRegex(ValueError, "max_snippets must be at least min_hits"):
            extractive_draft(
                rag, "shared evidence", tenant_id="tenant-a", principal_id="user-a",
                min_hits=4, max_snippets=3,
            )

    def test_invalid_minimum_evidence_count_is_rejected_before_retrieval(self):
        for invalid in (0, -1, True, "2"):
            with self.subTest(min_hits=invalid):
                with self.assertRaisesRegex(ValueError, "min_hits must be a positive integer"):
                    extractive_draft(
                        SecureDocRAG(), "query", tenant_id="tenant-a",
                        principal_id="user-a", min_hits=invalid,
                    )

    def test_invalid_snippet_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            extractive_draft(SecureDocRAG(), "x", tenant_id="tenant-a",
                             principal_id="user-a", max_snippets=0)


if __name__ == "__main__":
    unittest.main()
