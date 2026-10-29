# evidence/aws/aws-remediation-vpc-rds

Static, credential-free evidence for branch `aws-remediation-vpc-rds`. Nothing was deployed; no AWS credentials were
present (run-cmd.sh unsets them and points AWS config/credential files at /dev/null). Not a certification.

- `COMMANDS.tsv`: every logged command (UTC start, exit code, duration, log, cwd, command), including failures.
- `logs/`: full output of each command. `pass0-nag/`, `pass1-nag/`: nag reports from the failing passes.
- `synth/`: final synthesized templates + manifest (`cdk synth --no-lookups`, env-agnostic).
- `cdk-nag/`: final AwsSolutions + NIST 800-53 R5 reports and validation-report.json.
- `jest-results.json`: final Jest results (36 tests incl. negative controls; pass 4, B5-2).
- `superseded/pass3-pre-B5-2/`: the pass-3 synth, cdk-nag and Jest outputs (33 tests), kept unmodified after pass 4 replaced them.
- `SECURITY_EXCEPTIONS.md`: proposed exceptions EX-01..EX-04. `CORRECTION_PASSES.md`: what failed and what changed.
- `SHA256SUMS`: `sha256sum -c SHA256SUMS` from this directory.

Second nag pack: no prior repo context named HIPAA, NIST or PCI, so NIST 800-53 Rev 5 was used.
