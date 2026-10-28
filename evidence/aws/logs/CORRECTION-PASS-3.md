# Correction pass 3 (final allowed)
Failure (log 15 pass3): test bug only. In env-agnostic stacks `Stack.account` is an unresolved token string
(`${Token[AWS.AccountId.N]}`), not a literal containing "AWS::AccountId". Synth (log 16) already exit 0 with
manifest environment `aws://unknown-account/unknown-region` and all cdk-nag rules Compliant.
Fix: assert `Token.isUnresolved(stack.account/region)`. Stack code unchanged.
