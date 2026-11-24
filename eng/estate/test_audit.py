"""Regression controls for the estate receipt boundary."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

import audit


class EstateReceiptTests(unittest.TestCase):
    def run_fixture(self, value, exit_code, name="BashAssay", **extra):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            command = [sys.executable, "-c", f"print({json.dumps(value)!r})\nraise SystemExit({exit_code})"]
            step = {"scope": "fixture", "argv": command, "receipt": {"format": "playground"}, **extra}
            return audit.run_step(name, step, directory, directory, 1)

    def receipt(self, verdict="Pass", name="BashAssay"):
        return {"schemaVersion": "canonflow.assay.playground-receipt/v2",
                "repository": name, "verdict": verdict}

    def test_producer_failure_stays_failed(self):
        result = self.run_fixture(self.receipt("Fail"), 1)
        self.assertEqual(result["verdict"], "Fail")
        self.assertIn("sha256", result["receipt"])

    def test_incomplete_producer_stays_inconclusive(self):
        self.assertEqual(self.run_fixture(self.receipt("Inconclusive"), 2)["verdict"], "Inconclusive")

    def test_pass_and_exit_must_agree(self):
        self.assertEqual(self.run_fixture(self.receipt(), 1)["verdict"], "ToolFailure")

    def test_untrusted_old_wrapper_is_rejected(self):
        receipt = self.receipt()
        receipt["schemaVersion"] = "canonflow.assay.playground-receipt/v1"
        self.assertEqual(self.run_fixture(receipt, 0)["verdict"], "ToolFailure")

    def test_receipt_must_bind_the_named_repository(self):
        result = self.run_fixture(self.receipt(name="OtherAssay"), 0)
        self.assertEqual(result["verdict"], "ToolFailure")

    def test_zero_tests_are_inconclusive(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            step = {"scope": "fixture", "argv": [sys.executable, "-c", "print('# tests 0')"],
                    "testCountPattern": r"^# tests [1-9][0-9]*$"}
            self.assertEqual(audit.run_step("BashAssay", step, directory, directory, 1)["verdict"],
                             "Inconclusive")

    def test_reduction_preserves_known_failure_with_missing_evidence(self):
        self.assertEqual(audit.worst(["Pass", "Fail", "Inconclusive"]), "Fail")


if __name__ == "__main__":
    unittest.main()
