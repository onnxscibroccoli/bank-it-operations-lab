# Static asset and architecture inventory

`assets.json` and `ARCHITECTURE.md` are derived from the committed CDK-synthesized templates in `evidence/aws/aws-remediation-vpc-rds/synth`. They are not a discovery scan of a live account. Source SHA-256 hashes bind every record to its input template.

Run `python3 inventory/generate.py --check` to detect drift. Run without `--check` to regenerate after reviewing template changes. Tests: `python3 -m unittest discover -s inventory/tests`.

References, GetAtt and DependsOn are shown. Parameter values, implicit service dependencies and Fn::Sub strings are not interpreted. The existing AWS synthesis workflow compares fresh output to committed templates; the inventory check then compares those templates to the generated files.
