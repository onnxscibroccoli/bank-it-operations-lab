import json
import unittest

from _helpers import ROOT, TmpMixin, copytree, non_pass, reseal_listed, by_id
from acceptance.modules import aws_cdk


class AwsAdapterTest(TmpMixin, unittest.TestCase):
    def ev(self):
        return copytree(aws_cdk.EVIDENCE, self.td)

    def test_committed_evidence_passes(self):
        r = aws_cdk.run()
        d = r.to_dict()
        self.assertEqual(d["status"], "PASS", non_pass(r))
        self.assertEqual({c["id"] for c in d["checks"]},
                         {"AWS-INT-001", "AWS-JEST-001", "AWS-NAG-001", "AWS-NAG-002", "AWS-S3-001"})
        self.assertGreaterEqual(len(d["evidence"]), 8)  # SUMS + jest + 4 nag + 2 templates
        self.assertEqual(d["source"]["prs"][0], 5)

    # --- negatives: each must fail for exactly its intended reason
    def test_tampered_evidence_fails_on_hash(self):
        ev = self.ev()
        (ev / "logs/08-pass3-jest.log").write_text("tampered\n")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-INT-001": "EVIDENCE_HASH_MISMATCH"})
        self.assertIn("mismatch", by_id(r)["AWS-INT-001"].detail)

    def test_non_compliant_nag_row_fails_for_nag(self):
        ev = self.ev()
        p = ev / "cdk-nag/AwsSolutions--BankItLabNetworkDatabase-NagReport.csv"
        p.write_text(p.read_text() + '"AwsSolutions-RDS3","BankItLabNetworkDatabase/Db/Resource","Non-Compliant","N/A","Error","x"\n')
        reseal_listed(ev / "SHA256SUMS")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-NAG-002": "NAG_NON_COMPLIANT"})
        self.assertIn("AwsSolutions-RDS3", by_id(r)["AWS-NAG-002"].detail)

    def test_missing_nag_report_fails_for_count(self):
        ev = self.ev()
        (ev / "cdk-nag/NIST.800.53.R5--BankItLabSecureStorage-NagReport.csv").unlink()
        reseal_listed(ev / "SHA256SUMS")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-NAG-001": "NAG_REPORT_COUNT"})

    def test_failed_jest_run_fails_for_unit_tests(self):
        ev = self.ev()
        p = ev / "jest-results.json"
        d = json.loads(p.read_text())
        d.update(success=False, numFailedTests=1, numPassedTests=d["numPassedTests"] - 1)
        p.write_text(json.dumps(d))
        reseal_listed(ev / "SHA256SUMS")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-JEST-001": "UNIT_TESTS_FAILED"})

    def test_missing_negative_controls_suite_fails_for_unit_tests(self):
        ev = self.ev()
        p = ev / "jest-results.json"
        d = json.loads(p.read_text())
        d["testResults"] = [t for t in d["testResults"] if "negative-controls" not in t["name"]]
        p.write_text(json.dumps(d))
        reseal_listed(ev / "SHA256SUMS")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-JEST-001": "UNIT_TESTS_FAILED"})
        self.assertIn("negative-controls.test.ts", by_id(r)["AWS-JEST-001"].detail)

    def test_self_logging_bucket_fails_for_s3_self_logging(self):
        ev = self.ev()
        p = next((ev / "synth").glob("BankItLabSecureStorage.template.json"))
        t = json.loads(p.read_text())
        bid, b = next((k, v) for k, v in t["Resources"].items() if v["Type"] == "AWS::S3::Bucket")
        b.setdefault("Properties", {})["LoggingConfiguration"] = {"DestinationBucketName": {"Ref": bid}}
        p.write_text(json.dumps(t, indent=1))
        reseal_listed(ev / "SHA256SUMS")
        r = aws_cdk.run(evidence_dir=ev)
        self.assertEqual(non_pass(r), {"AWS-S3-001": "S3_SELF_LOGGING"})
        self.assertIn(bid, by_id(r)["AWS-S3-001"].detail)

    def test_missing_bundle_fails_for_missing_evidence(self):
        r = aws_cdk.run(evidence_dir=self.td / "nope")
        self.assertEqual(r.to_dict()["reason_code"], "EVIDENCE_MISSING")


if __name__ == "__main__":
    unittest.main()
