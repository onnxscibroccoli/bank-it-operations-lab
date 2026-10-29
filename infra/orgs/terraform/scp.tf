locals {
  policy_dir = "${path.module}/../../../evidence/orgs/policies"
  scp_files  = fileset(local.policy_dir, "*.json")
}

resource "aws_organizations_policy" "guardrail" {
  for_each = local.scp_files
  name     = trimsuffix(each.value, ".json")
  type     = "SERVICE_CONTROL_POLICY"
  content  = file("${local.policy_dir}/${each.value}")
}

# Attachment is intentionally absent. Attaching an SCP is an Organizations mutation.
# The reference stops at the policy document.
