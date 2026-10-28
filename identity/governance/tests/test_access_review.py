"""access_review.py against synthetic accessReviewInstanceDecisionItem fixtures (offline)."""
import os
import unittest

import _common
import access_review as ar


class TestAccessReview(unittest.TestCase):
    def test_baseline_decisions_across_pages(self):
        rep = ar.run(os.path.join(_common.SCEN, "baseline"))
        self.assertEqual(rep["pages"], 2)
        self.assertEqual(rep["total"], 5)
        self.assertEqual(rep["decisions"], {"Approve": 2, "Deny": 2, "NotReviewed": 1, "DontKnow": 0})
        self.assertEqual([f["rule"] for f in rep["findings"]], ["AR-002", "AR-003", "AR-001"])
        self.assertEqual(rep["exitCode"], 1)

    def test_summarize_malformed_and_justification(self):
        counts, f = ar.summarize([{"id": "1"}, "x", {"id": "2", "decision": "Approve", "justification": " ",
                                                     "principal": {"id": "p"}, "reviewedBy": {"id": "r"}}])
        self.assertEqual(counts["Approve"], 1)
        self.assertEqual(sorted(x["rule"] for x in f), ["AR-004", "DQ-001", "DQ-001"])

    def test_auth_failure_fails_closed(self):
        rep = ar.run(os.path.join(_common.SCEN, "auth-401"), path="/roleManagement/directory/roleDefinitions"
                     "?$select=id,displayName,templateId,isBuiltIn")
        self.assertEqual((rep["exitCode"], rep["error"]["kind"]), (2, "authorization"))

    def test_unknown_instance_is_404_error(self):
        rep = ar.run(os.path.join(_common.SCEN, "baseline"), path=ar.decisions_path("x", "y"))
        self.assertEqual((rep["exitCode"], rep["error"]["status"]), (2, 404))


if __name__ == "__main__":
    unittest.main()
