# Infrastructure as code and routine automation

## Level 1: Everyday explanation

Infrastructure is the computing equipment and services applications rely on. Infrastructure as Code (IaC) describes those resources in files that can be reviewed and reused, rather than relying only on someone clicking through settings.

See the [IaC glossary entry](glossary.md#iac) and [Wikipedia introduction](https://en.wikipedia.org/wiki/Infrastructure_as_code).

Think of a building plan: checking the drawing can catch mistakes, but it does not prove the building exists or is safe in operation.

## Level 2: Operational explanation

Teams review proposed changes, estimate cost and impact, test changes, and decide how to recover if something goes wrong. Automation performs repeatable steps; a human still needs to define the allowed targets and success conditions. Patching updates software to address defects or vulnerabilities.

## Level 3: Engineering reference

[The AWS CDK module](../../infra/aws-cdk/README.md) produces cloud configuration templates and checks them without deployment. [Patch planning](../../operations/patching) and [hardening](../../operations/hardening) demonstrate policy and validation logic. Their presence does not establish that real machines were updated.

Reading these references needs no account. Running module tests requires their documented runtime dependencies. Cloud deployment can create costs and change access; no deployment command is part of this beginner page.

## Level 4: Evidence boundaries and troubleshooting

Inspect the module's package scripts, tests, generated evidence, and security exceptions together. A synthesized template proves neither connectivity nor a recoverable service. Missing dependencies are an environment problem, not evidence of a failed cloud deployment. Failed security checks require diagnosis and review, not suppression for appearance.

For agent work, find the exact validation command in each module README. Do not invent apply/deploy commands or use credentials. [Evidence and governance](governance.md) explains review responsibilities. A full executable IaC tutorial remains planned.
