"""Offline checks for optional model integration; no external requests."""
import unittest
from unittest.mock import patch
from bioreason.model import ask_model, ModelError


class ModelTests(unittest.TestCase):
    def test_unconfigured_model_refused(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ModelError):
                ask_model("Analyst", {})

    def test_plaintext_external_endpoint_refused(self):
        with self.assertRaises(ModelError):
            ask_model("Analyst", {}, endpoint="http://example.com/v1/chat/completions", model="demo")

    def test_credentials_in_endpoint_refused(self):
        with self.assertRaises(ModelError):
            ask_model("Analyst", {}, endpoint="https://user:pass@example.com/v1", model="demo")

    def test_non_dict_evidence_refused(self):
        with self.assertRaises(ModelError):
            ask_model("Analyst", [], endpoint="https://example.com/v1", model="demo")

    def test_oversized_evidence_refused(self):
        with self.assertRaises(ModelError):
            ask_model("Analyst", {"data": "x" * 51000}, endpoint="https://example.com/v1", model="demo")


if __name__ == "__main__":
    unittest.main()
