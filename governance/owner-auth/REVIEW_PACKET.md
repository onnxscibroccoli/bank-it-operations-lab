# Frozen review packet

This packet is for the delivery branch. It is not an approval and it does not make a candidate eligible.

| Identity | SHA |
|---|---|
| main | `7f50348bf1370381615eaed91c02607fe41de2f5` |
| PR #7 candidate, left unchanged | `a9d0f64f11bf5b43d2bd7fcd9a53f15483c75f45` |
| Delivery head when this packet was first added | `a5b60edcc886e9f389d814701b24d9d71a76df99` |
| Actions on that head | orgs-static, network-edge, backup-static, and the aws-cdk synth passed. The offline suite failed: the static inventory had not been regenerated after the backup-role change, and three coverage tests still assumed `orgs-security` was BLOCKED. |

Attestations, if any are later made, must name the exact final SHA. `a5b60ed` is not that SHA once this packet is amended. PR #1 was already closed before this amendment; closing it is not an acceptance of the replacement stack.

Last known integration-gate on the PR #7 candidate failed merge-eligibility. Execution jobs on earlier candidates were green. That result is not reused for this delivery head.

## Exception scopes, still PROPOSED

- EX-01: access-log bucket uses SSE-S3 because S3 log delivery cannot use a CMK. Risk: log objects are not under the lab CMK.
- EX-02: no cross-region replication. Risk: a region loss is not covered by this stack.
- EX-03: RDS enhanced monitoring log-stream names are chosen by AWS inside one log group. Risk: a wildcard on that group's streams.
- EX-04: narrowed. The AWS-managed backup policy is gone. The role may snapshot this instance and `awsbackup-*` snapshots, and the trust requires `aws:SourceAccount` plus `aws:SourceArn` of this vault. Risk that remains: the snapshot name wildcard. It is not approved.

## Organizations

B6-1, B6-2, and B6-3 are repaired in this delivery tree (terminal log sink, no role exemption, Terraform track). They are static. Nothing was applied in an AWS account.

## What a reviewer would be approving if they later approve a SHA

A reference lab. Not a production bank network. Not a certification. SIMULATION and PLAN_ONLY labels still mean what they say.

## What is still unmet

AC1, AC2, AC4, AC5. The allow-list has no user. No owner key is enrolled. Branch protection is not turned on, because requiring a second approval with no second identity would lock `main`.
