# Troubleshooting

Start with the symptom you see. Each entry gives the likely cause, how to confirm it, and the safe fix. None of these fixes involves editing evidence or weakening a check. If a check fails, the failure is the result to report.

## The documentation site

**Search says "Search could not load".** The browser could not fetch `search-index.json`. Usually the site was opened as a file (`file://...`) instead of over HTTP. Serve it with `python3 -m http.server 8000 --bind 127.0.0.1 --directory dist/docs` and open `http://127.0.0.1:8000`. The full catalog on the home page still works without search. The browser check confirms this fallback message appears when the index is blocked.

**Search finds nothing.** The message says no matching documents were found, which does not mean the topic is absent. Try fewer words, clear the Subject, Status and Depth filters, or use [Browse topics](topics.md). Ranking is word and alias matching only, not meaning.

**Search needs JavaScript.** It does. Every page, the navigation and the catalog work without it.

**A page works locally but returns 404 on GitHub Pages.** GitHub's Pages artifact upload skips hidden directories, so pages under a dot-prefixed folder such as `.github/` used to be missing from the live site. The builder now writes such pages under `dot-` names, for example `pages/dot-github/pull_request_template.html`. If you see a new 404, check whether its URL contains a segment starting with `.`.

**The build fails with "Missing metadata".** A new Markdown file has no entry in `docs/metadata/pages.json`. Add an entry that meets `docs/metadata/schema.json`. Do not delete the file to make the build pass.

**The build fails with "Broken curated links".** A link on a non-archived page points to a file that does not exist. Fix the link. Archived pages are reported in `coverage.json` but do not fail the build.

**A test says a preserved record changed.** `test_frozen_records_unchanged` found a byte change in a file listed in `docs/metadata/preserved-records.json`. Revert the change and put new explanation in sidecar metadata or a new page. Do not update the digest just to silence the test.

**Playwright cannot launch Chromium.** Run `npx --prefix scripts/docs playwright install --with-deps chromium`. Without root, drop `--with-deps`; it may still fail if system libraries are missing. CI pins Ubuntu 24.04 for this reason.

**The axe check cannot inject its script on a page.** On GitHub Pages this happened because the page was a 404 error page that sets a strict Content-Security-Policy. Treat it as a missing page first.

## Exercises and module checks

**`No such file or directory`.** You are probably not in the repository root. Run `git rev-parse --show-toplevel` and `cd` there.

**The health evaluation says UNHEALTHY or stale.** Without `--now 2026-10-28T12:01:00Z`, the saved observation is old compared with your clock. A stale result is correct behavior, not a bug.

**The restore verifier says REJECTED.** Read every `ERROR` line. Common causes are a modified file (hash mismatch) or a malformed row. If you did not modify the bundle, report it. `artifacts: NOT CHECKED` alone is expected, since dumps live in CI artifacts.

**The incident timeline verifier fails with `FileNotFoundError ... events.jsonl`.** You passed the `.console` directory. Pass the run directory without `.console`.

**The incident demo or live restore will not start.** They need PostgreSQL server binaries (`initdb`, `pg_ctl`, `postgres`), and cluster initialization must not run as root. Client tools such as `psql` are not enough.

**`npm ci` fails in a CDK module.** It needs network access to the npm registry and Node 20 or newer. A missing dependency is an environment problem, not a failed deployment, and nothing is deployed either way.

**A security check fails (for example a cdk-nag or guard test).** Diagnose it and record it. Suppressing it requires an approved exception (see the [AWS CDK exception register](../../evidence/aws/aws-remediation-vpc-rds/SECURITY_EXCEPTIONS.md) and [ADR 0005](../adr/0005-scoped-security-exception-register.md)); a documentation change cannot approve one.

## Still not covered

- Troubleshooting for the Organizations Terraform track and the hybrid Windows runbooks (both NOT_EXECUTED) is limited to their own READMEs.
- Screen reader-specific problems have not been collected, because no screen reader test has been run. See [Accessibility verification](accessibility.md).
