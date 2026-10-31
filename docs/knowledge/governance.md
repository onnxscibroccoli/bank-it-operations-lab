# Read evidence and govern operational changes

## Level 1: Everyday explanation

Evidence is information that supports a claim. A receipt proves a purchase was recorded; it does not prove the purchased item still works. Similarly, a passing test supports the behavior it checked at that time.

## Level 2: Operational explanation

Change control records what will change, who is responsible, what could go wrong, and how to verify the result. An access review asks whether existing permissions are still justified. An audit examines records against stated criteria.

A useful change record identifies its owner, affected services, test scope, rollback plan, and approval. A lab can demonstrate those records without establishing production experience or regulatory compliance.

## Level 3: Repository evidence

[The module registry](../../coordination/modules.json) records implementation paths and checks. [Remaining owner actions](../../reports/USER_ACTIONS_REQUIRED.md) records unresolved decisions. INTEGRATED is a repository assembly label, not production verification or approval.

Check the tested revision, environment, command, exit code, and raw output. Preserve failed runs. A test that expects a failure must check the reason, not simply accept any error.

## Level 4: Regulatory boundaries

General IT controls can support regulated work, but applicability depends on jurisdiction, institution type, and the specific obligation. Binding requirements and supervisory guidance are distinct. This introductory page makes no legal interpretation or compliance certification; the existing control mappings require source and applicability review before operational use.

## Practical review and agent guidance

Reading is safe and needs no tools. Pick one capability and locate its source, tests, and evidence. If a link or artifact is missing, record that gap. Never invent an approval, promote maturity automatically, or use a PR title as proof. Consult [current development](development.md) and the [metadata standard](standards.md).
