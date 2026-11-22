import unittest

from grounded_response import extractive_draft
from secure_doc_rag_agent import Chunk, RetrievalAuthorization, SecureDocRAG


class GroundedResponseTests(unittest.TestCase):
    def test_draft_preserves_citations(self):
        rag = SecureDocRAG()
        rag.add(Chunk("c1", "invoice-1", "Gross weight is 1200 kg."))
        draft = extractive_draft(rag, "gross weight")
        self.assertTrue(draft.sufficient_evidence)
        self.assertEqual(draft.citations, ("invoice-1#c1",))
        self.assertIn("1200", draft.answer)

    def test_insufficient_evidence_returns_no_answer(self):
        rag = SecureDocRAG()
        rag.add(Chunk("c1", "one", "shipment delayed"))
        draft = extractive_draft(rag, "shipment delayed", min_hits=2)
        self.assertFalse(draft.sufficient_evidence)
        self.assertIsNone(draft.answer)

    def test_sensitive_draft_requires_explicit_authorization(self):
        rag = SecureDocRAG()
        rag.add(Chunk("c1", "private", "passport number 12345", sensitivity="private"))
        denied = extractive_draft(rag, "passport number")
        self.assertFalse(denied.sufficient_evidence)
        allowed = extractive_draft(
            rag,
            "passport number",
            authorization=RetrievalAuthorization("reviewer", "default", ("private",)),
        )
        self.assertTrue(allowed.sufficient_evidence)

    def test_max_snippets_must_be_positive(self):
        rag = SecureDocRAG()
        with self.assertRaisesRegex(ValueError, "max_snippets"):
            extractive_draft(rag, "query", max_snippets=0)


if __name__ == "__main__":
    unittest.main()
