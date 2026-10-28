# Correction pass 1
Failure (logs 05/06/08 pass1): cdk-nag 3.0.2 `AwsSolutionsChecks` is a Validations plugin (constructor(scope, props)), not an IAspect.
The BANK-AWS-001 spec requires `Aspects.of(app).add(new AwsSolutionsChecks({verbose:true}))` and CSV/JSON NagReports in cdk.out,
which is the cdk-nag v2 API. Fix: pin cdk-nag 2.38.2 (latest 2.x; peer aws-cdk-lib ^2.176.0). No code change to stack.
Open question: migrate to cdk-nag v3 Validations API later (would change report format to policy-validation-report.json).
