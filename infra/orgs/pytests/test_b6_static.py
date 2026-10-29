"""Static checks for the Organizations reference. Stdlib only. No AWS calls.

B6-1: the access-log bucket is a terminal sink.
B6-2: exported SCP documents contain no principal-ARN exemption.
B6-3: a Terraform track exists and points at those documents.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICIES = ROOT / "evidence" / "orgs" / "policies"
TF = ROOT / "infra" / "orgs" / "terraform"


class OrganizationsStatic(unittest.TestCase):
    def test_scp_documents_exported_and_not_exempting_roles(self):
        files = sorted(POLICIES.glob("*.json"))
        self.assertGreaterEqual(len(files), 6, "run npm run export:policies in infra/orgs")
        blob = "\n".join(p.read_text() for p in files)
        self.assertNotIn("ArnNotLike", blob)
        self.assertNotIn("OrgBreakGlass", blob)
        self.assertNotIn("OrgSecurityAdmin", blob)
        for p in files:
            doc = json.loads(p.read_text())
            self.assertEqual(doc["Version"], "2012-10-17")
            for statement in doc["Statement"]:
                self.assertEqual(statement["Effect"], "Deny")

    def test_terraform_track_reads_exported_policies_and_does_not_self_log(self):
        scp = (TF / "scp.tf").read_text()
        self.assertIn("aws_organizations_policy", scp)
        self.assertIn("evidence/orgs/policies", scp)
        self.assertNotIn("aws_organizations_policy_attachment", scp)
        logging = json.loads((TF / "cloudtrail_logging.tf.json").read_text())
        logs = logging["resource"]["aws_s3_bucket_logging"]
        self.assertEqual(list(logs), ["trail"])
        self.assertNotIn("trail_access_logs", logs)
        target = logs["trail"]["target_bucket"]
        self.assertIn("trail_access_logs", target)
        self.assertNotIn("aws_s3_bucket.trail.id", target)

    def test_bucket_key_option_is_not_a_bucket_resource_attribute(self):
        resources = json.loads((TF / "cloudtrail_logging.tf.json").read_text())["resource"]
        for resource in resources["aws_s3_bucket"].values():
            self.assertNotIn("bucket_key_enabled", resource)

    def test_cdk_source_has_no_self_log_prefix_on_the_sink(self):
        text = (ROOT / "infra" / "orgs" / "lib" / "org-cloudtrail-stack.ts").read_text()
        sink, _, trail = text.partition("const bucket = new s3.Bucket")
        sink_code = "\n".join(line for line in sink.splitlines() if not line.strip().startswith("//") and not line.strip().startswith("*"))
        self.assertNotIn("serverAccessLogsPrefix", sink_code)
        self.assertIn("serverAccessLogsBucket: accessLogs", trail)


if __name__ == "__main__":
    unittest.main()
