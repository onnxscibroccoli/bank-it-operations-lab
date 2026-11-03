import unittest

from _helpers import ROOT  # noqa: F401  (sets sys.path)
from acceptance.modules.contract import Check, ModuleResult, check, validate, CONTRACT_ID


def mk(*checks):
    r = ModuleResult("x", "a@0", {"prs": [], "paths": []}, "static-evidence")
    for c in checks:
        r.add(c)
    return r


class ContractTest(unittest.TestCase):
    def test_pass_result_validates(self):
        d = mk(check("A", "t", "positive", True, "RUN_FAILED")).to_dict()
        self.assertEqual((d["contract"], d["status"], d["reason_code"], d["reason_codes"]),
                         (CONTRACT_ID, "PASS", "OK", []))

    def test_fail_reason_is_first_failing_check(self):
        d = mk(check("A", "t", "positive", True, "RUN_FAILED"),
               check("B", "t", "negative", False, "NEGATIVE_WRONG_REASON"),
               check("C", "t", "integrity", False, "EVIDENCE_HASH_MISMATCH")).to_dict()
        self.assertEqual(d["status"], "FAIL")
        self.assertEqual(d["reason_code"], "NEGATIVE_WRONG_REASON")
        self.assertEqual(d["reason_codes"], ["NEGATIVE_WRONG_REASON", "EVIDENCE_HASH_MISMATCH"])

    def test_no_checks_is_not_executed_never_pass(self):
        self.assertEqual(mk().status, "NOT_EXECUTED")

    def test_only_not_executed_is_not_pass(self):
        r = mk(check("A", "t", "positive", False, "TOOL_UNAVAILABLE", status_if_fail="NOT_EXECUTED"))
        self.assertEqual(r.status, "NOT_EXECUTED")

    def test_failed_check_without_reason_rejected(self):
        with self.assertRaises(AssertionError):
            Check("A", "t", "positive", "FAIL", "OK")

    def test_unknown_reason_rejected(self):
        with self.assertRaises(AssertionError):
            Check("A", "t", "positive", "FAIL", "SOMETHING_ELSE")

    def test_claims_must_be_false(self):
        d = mk(check("A", "t", "positive", True, "RUN_FAILED")).to_dict()
        d["claims"]["cloud_mutated"] = True
        with self.assertRaisesRegex(ValueError, "never claim"):
            validate(d)

    def test_pass_with_non_ok_reason_rejected(self):
        d = mk(check("A", "t", "positive", True, "RUN_FAILED")).to_dict()
        d["reason_code"] = "RUN_FAILED"
        with self.assertRaisesRegex(ValueError, "PASS must carry"):
            validate(d)


if __name__ == "__main__":
    unittest.main()
