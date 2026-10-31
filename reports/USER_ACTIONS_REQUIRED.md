# What you need to do manually

Development, commits and Actions runs are already authorized. You do not need to buy more bot usage or give another generic permission to continue. PR #35 is the current draft delivery. PR #1 has already been closed; there is nothing for you to close.

## 1. Invite an independent human reviewer

1. Choose a person who can review the code and is not the author account used by the agents. A second account controlled by you does not create an independent technical review.
2. Sign into GitHub as the repository owner and open https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/access . Alternatively open the repository, click **Settings**, then **Collaborators** under Access.
3. Click **Add people**, enter their exact GitHub username, select the matching account, and send the invitation.
4. Have them accept the invitation. This is collaborator access on a personal repository; do not look for a second Admin role or transfer the repository.
5. Tell the integrator their username. The integrator can prepare the allow-list and CODEOWNERS changes; the reviewer must inspect the trusted-gate bootstrap separately before those changes become trusted.
6. Once the final candidate is frozen and ready for review, the reviewer opens PR #35, reads **Files changed** and the Actions results, then uses **Review changes > Approve > Submit review** only if satisfied. Record the exact full commit SHA reviewed. A later code change requires fresh review. An approval on old PR #7 does not approve PR #35.

## 2. Protect both branches

These are repository-owner settings. Creating rules does not itself approve code. Have the reviewer available before enforcing rules so the protected PR route can be used.

1. Open https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/rules .
2. Click **New ruleset > New branch ruleset**. Name it `protect-main`, set enforcement to **Active**, and leave the bypass list empty.
3. Under target branches, include the branch pattern `main`.
4. Enable **Restrict deletions**, **Block force pushes**, **Require a pull request before merging**, **1 required approval**, **Dismiss stale approvals**, **Require approval of the most recent reviewable push**, and **Require conversation resolution**.
5. Require Code Owner review once the reviewed CODEOWNERS file naming the real reviewer is present. An invented or empty reviewer name cannot supply this protection.
6. Enable required status checks and require the branch to be up to date. Select the actual `final-summary` and `merge-eligibility` check contexts from the integration-gate run, with GitHub Actions as source. Match the displayed check names exactly; do not paste unverified workflow/job combinations. The integrator must also wire the portfolio validation into the trusted acceptance policy before it can represent the added modules.
7. Click **Create**. Reopen the rule and confirm it is Active and targets `main`.
8. Create a second rule named `protect-acceptance`, targeting exactly `evidence/acceptance`. Require a PR, one independent approval, stale-review dismissal, conversation resolution, no force pushes and no deletion. Leave bypass empty. Require Code Owner review after the corresponding file is present on that branch.
9. Do not enable **Restrict updates** without a reviewed, working update route: an empty permitted route can prevent the needed evidence PR from landing. Confirm direct pushes are rejected and the reviewed PR route works.

If a check is absent from the picker, the integrator needs to run its workflow and verify the context. Do not substitute a convenient green check. Branch rules alone do not prevent a malicious candidate from redefining a job: the trusted, independently reviewed workflow/config/manifest bootstrap is also required. Do not merge an ineligible candidate to bootstrap itself.

## 3. Review the risks; wait for a usable owner-signing path

Open `evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md` on the delivery branch. For each exception, decide whether you accept the described limitation, reject it, or require changes:

- EX-01: access logs use S3-managed encryption rather than a customer-managed KMS key.
- EX-02: the lab does not configure cross-region replication.
- EX-03: RDS monitoring permission includes a bounded log-stream wildcard.
- EX-04: backup uses a bounded snapshot-name wildcard; **the vault-scoped service-role trust also remains unverified at runtime and blocks deployment**.

You can discuss those choices in plain language now. They are not effective gate approvals yet. The integrator must provide a frozen packet containing the exact candidate, main, tested-merge SHA, Actions run and current exception scope, plus the reviewed authentication procedure. Old EX-04 scopes and old SHA templates are obsolete.

Do not create a second Admin account, paste private keys into chat, or post placeholder attestations. The owner-signature verifier is implemented and tested but not activated. Its remaining adapter and policy work is engineering work, not a task you are expected to solve manually. Once reviewed, enrollment must keep your signing private key outside agent access. A signed owner decision will still not replace the independent reviewer in step 1.

## 4. Confirm the lab's identity-policy assumptions

Read `evidence/entra/BASELINE-CHOICES-PENDING.md` and PR #4. Decide whether the lab should keep risk policies report-only, apply device compliance to All users/All apps, and use the listed 12 privileged roles. Tell the integrator which choices you want retained or changed. This is approval of a synthetic lab design, not permission to apply policies to a live tenant. Formal AC4/AC5 acceptance still requires the frozen packet and working owner-authentication path above.

## 5. View the package and give final acceptance later

1. Open https://github.com/onnxscibroccoli/bank-it-operations-lab/actions/workflows/portfolio-validation.yml .
2. Select the successful run for the latest PR #35 commit. Check that its SHA matches the commit you intend to inspect.
3. Scroll to **Artifacts** and download the portfolio package. Sign in if GitHub requests it. Check its COMMIT and checksum files, then follow README and the 15-minute demo.
4. The package is a draft lab deliverable. Final human acceptance waits until the required review, protection and applicable acceptance gates are complete. No live deployment is requested.

Official UI references: [invite a collaborator](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository), [create a ruleset](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).
