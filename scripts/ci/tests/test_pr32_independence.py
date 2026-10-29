"""PR #32 regressions on candidate 5a75d9c.
D1: AC4/AC5 (and exception) attestations from the PR author never count; workflow_run must be a completed, successful
    integration-gate run (name + path; all jobs green except the fail-closed merge-eligibility) of the candidate or an
    attested tested merge.
D2: owner decisions are owner-LOGIN-bound; when the owner login is the PR author / shared account they are
    INSUFFICIENT_INDEPENDENCE (blocking) until a separate owner identity exists (O-5 / UA-6).
D3: the gate pin must be an independently reviewed gate commit, never the candidate; otherwise TRUSTED GATE UNVERIFIED
    and NOT ELIGIBLE."""
import copy, json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_exceptions, reviews, verify_trusted_gate as vtg  # noqa: E402
from test_merge_eligibility_binding import (APPROVED_REVIEWS, AUTHOR, CAND, CONFIG, IDENT, MERGE, OWNER, REVIEWER,  # noqa: E402
                                            attestation, gate_run, run)

ROOT = Path(__file__).resolve().parents[3]
EXC = check_exceptions.evaluate(ROOT)
SCOPES = reviews.exception_scopes(EXC)
REAL_CONFIG = json.loads((ROOT / ".github/acceptance/trusted-config.json").read_text())
OTHER = "b908a669b302ff37f2c2ca79ed828f65e5a9f432"
GATE = "ce69f84b3333e1d8da99deb03d17f1457464d962"


def rv(**over):
    r = copy.deepcopy(APPROVED_REVIEWS); r.update(over); return r


def exc_att(ex, login=OWNER, decision="APPROVED", cid=None):
    return attestation(login, "EXCEPTION", decision, cid=cid or 200 + int(ex[-2:]), at="2026-10-28T23:20:00Z",
                       extra=(f"exception: {ex}", f"scope: {SCOPES[ex]}"))


def full_set(login):
    return [exc_att(ex, login) for ex in sorted(SCOPES)] + [attestation(login, "AC4", "ACCEPT", cid=301), attestation(login, "AC5", "ACCEPT", cid=302)]


class D1AuthorExcludedAndRunVerified(unittest.TestCase):
    def test_full_self_posted_author_set_stays_not_eligible(self):
        for cfg in (CONFIG, dict(CONFIG, owner_logins=[AUTHOR]), dict(CONFIG, owner_logins=[AUTHOR], reviewer_allowlist=[REVIEWER, AUTHOR])):
            with self.subTest(owners=cfg["owner_logins"], allow=cfg["reviewer_allowlist"]):
                r = rv(comments=full_set(AUTHOR))
                d = reviews.decisions_from_comments(r, IDENT, cfg, EXC)
                self.assertEqual({k: d[k][0] for k in ("AC2", "AC4", "AC5")}, {"AC2": "UNMET", "AC4": "UNMET", "AC5": "UNMET"})
                self.assertEqual(set(d["exceptions"].values()), {"INSUFFICIENT_INDEPENDENCE"})
                rc, out = run(reviews=r, exc=EXC, config=cfg)
                self.assertEqual(rc, 1)
                self.assertIn("NOT ELIGIBLE", out)
                self.assertIn("INSUFFICIENT", out)

    def test_author_case_variant_is_still_the_author(self):
        d = reviews.decisions_from_comments(rv(comments=[attestation(AUTHOR.upper(), "AC4", "ACCEPT")]), IDENT,
                                            dict(CONFIG, owner_logins=[AUTHOR]), EXC)
        self.assertEqual(d["AC4"][0], "UNMET")

    def test_unknown_pr_author_fails_closed(self):
        d = reviews.decisions_from_comments(rv(pr_author=None, comments=[attestation(REVIEWER, "AC4", "ACCEPT")]), IDENT, CONFIG, EXC)
        self.assertEqual(d["AC4"][0], "UNMET")

    def bad_runs(self):
        return {
            "failed job besides merge-eligibility": gate_run(jobs=[{"name": "final-summary", "conclusion": "success"},
                                                                   {"name": "aws-cdk / synth-and-test", "conclusion": "failure"},
                                                                   {"name": "merge-eligibility", "conclusion": "failure"}]),
            "final-summary failed": gate_run(jobs=[{"name": "final-summary", "conclusion": "failure"}]),
            "other workflow name": gate_run(name="offline-validation", path=".github/workflows/offline-validation.yml"),
            "same name, other path": gate_run(path=".github/workflows/fake-gate.yml"),
            "in progress": gate_run(status="in_progress", conclusion=None),
            "cancelled, no jobs": gate_run(conclusion="cancelled", jobs=[]),
            "run of another commit": gate_run(head=OTHER),
            "fetch error": {"error": "HTTPError: 404"},
            "not fetched": None,
        }

    def test_failed_or_other_workflow_run_ref_is_ignored(self):
        for why, r in self.bad_runs().items():
            with self.subTest(why=why):
                d = reviews.decisions_from_comments(rv(comments=[attestation(REVIEWER, "AC4", "ACCEPT")],
                                                       runs={} if r is None else {"40800364073": r}), IDENT, CONFIG, EXC)
                self.assertEqual(d["AC4"][0], "UNMET", why)

    def test_controls_successful_run_and_main_validation_run_count(self):
        for r in (gate_run(), gate_run(conclusion="success", jobs=[]), gate_run(head=MERGE),
                  gate_run(path=".github/workflows/integration-gate.yml@refs/pull/7/merge")):
            with self.subTest(run=r):
                d = reviews.decisions_from_comments(rv(comments=[attestation(REVIEWER, "AC4", "ACCEPT")], runs={"40800364073": r}),
                                                    IDENT, CONFIG, EXC)
                self.assertEqual(d["AC4"][0], "MET_AT_RUNTIME", d["AC4"][1])


class D2OwnerLoginBound(unittest.TestCase):
    def test_shared_owner_login_is_insufficient_independence_and_labelled(self):
        d = reviews.decisions_from_comments(rv(comments=full_set(AUTHOR)), IDENT, dict(CONFIG, owner_logins=[AUTHOR]), EXC)
        text = " ".join(d["AC2"][1])
        self.assertIn("owner-login-bound", text)
        self.assertIn("NOT owner-authenticated", text)
        self.assertIn("O-5", text)
        self.assertNotIn("owner-authenticated by", text)

    def test_real_trusted_config_owner_is_the_pr_author(self):
        # The repository's trusted config today: owner_logins == [onnxscibroccoli] == PR #7 author -> blocking.
        self.assertIn(AUTHOR, [x.lower() for x in REAL_CONFIG["owner_logins"]])
        d = reviews.decisions_from_comments(rv(comments=full_set(AUTHOR)), IDENT, REAL_CONFIG, EXC)
        self.assertEqual(d["AC2"][0], "UNMET")
        self.assertTrue(all(s == "INSUFFICIENT_INDEPENDENCE" for s in d["exceptions"].values()), d["exceptions"])

    def test_control_distinct_owner_identity_meets_ac2(self):
        d = reviews.decisions_from_comments(rv(comments=full_set(OWNER)), IDENT, CONFIG, EXC)
        self.assertEqual(d["AC2"][0], "MET_AT_RUNTIME", d["AC2"][1])

    def test_owner_on_allowlist_cannot_verify_conditions_when_author(self):
        cond = attestation(OWNER, "EXCEPTION", "APPROVED_WITH_CONDITIONS", cid=250, at="2026-10-28T23:20:00Z",
                           extra=("exception: EX-04", f"scope: {SCOPES['EX-04']}", "conditions: x"))
        ver = attestation(AUTHOR, "EXCEPTION", "CONDITIONS_VERIFIED", cid=251, at="2026-10-28T23:40:00Z",
                          extra=("exception: EX-04", f"scope: {SCOPES['EX-04']}"))
        base = [exc_att(ex) for ex in ("EX-01", "EX-02", "EX-03")]
        d = reviews.decisions_from_comments(rv(comments=base + [cond, ver]), IDENT, dict(CONFIG, reviewer_allowlist=[REVIEWER, AUTHOR]), EXC)
        self.assertEqual(d["AC2"][0], "UNMET")


def review(state="APPROVED", commit=GATE, login=REVIEWER, rid=55):
    return {"id": rid, "state": state, "commit_id": commit, "user": {"login": login}}


MAN = {"gate_sha": GATE, "independent_review": {"pr": 40, "review_id": 55}}


class D3IndependentPin(unittest.TestCase):
    def test_control_independently_reviewed_pin_is_verified(self):
        self.assertEqual(vtg.pin_trust(MAN, CAND, CONFIG, review(), AUTHOR, "write")[0], "VERIFIED")

    def test_self_pin_is_unverified_even_if_reviewed(self):
        st, why = vtg.pin_trust(dict(MAN, gate_sha=CAND), CAND, CONFIG, review(commit=CAND), AUTHOR, "write")
        self.assertEqual(st, "UNVERIFIED")
        self.assertIn("self-pin", " ".join(why))

    def test_no_recorded_review_is_unverified(self):
        for man in ({"gate_sha": GATE}, {"gate_sha": GATE, "independent_review": None}, {"gate_sha": GATE, "independent_review": {"pr": 40}}):
            with self.subTest(man=man):
                self.assertEqual(vtg.pin_trust(man, CAND, CONFIG, None, None, None)[0], "UNVERIFIED")

    def test_unqualified_reviews_are_unverified(self):
        cases = {"by the PR author": (review(login=AUTHOR), dict(CONFIG, reviewer_allowlist=[AUTHOR]), "admin"),
                 "not allow-listed": (review(login="random-user"), CONFIG, "write"),
                 "read permission": (review(), CONFIG, "read"),
                 "other commit": (review(commit=OTHER), CONFIG, "write"),
                 "commented only": (review(state="COMMENTED"), CONFIG, "write"),
                 "dismissed": (review(state="DISMISSED"), CONFIG, "write"),
                 "fetch error": ({"error": "HTTPError: 404"}, CONFIG, None)}
        for why, (r, cfg, perm) in cases.items():
            with self.subTest(why=why):
                self.assertEqual(vtg.pin_trust(MAN, CAND, cfg, r, AUTHOR, perm)[0], "UNVERIFIED")

    def test_bad_manifest_or_unknown_candidate_is_unverified(self):
        self.assertEqual(vtg.pin_trust({}, CAND, CONFIG, review(), AUTHOR, "write")[0], "UNVERIFIED")
        self.assertEqual(vtg.pin_trust(MAN, None, CONFIG, review(), AUTHOR, "write")[0], "UNVERIFIED")

    def test_unverified_or_missing_gate_trust_is_not_eligible_even_when_all_acs_met(self):
        comments = full_set(OWNER)[:4] + [attestation(REVIEWER, "AC4", "ACCEPT", cid=301), attestation(REVIEWER, "AC5", "ACCEPT", cid=302)]
        rc, out = run(reviews=rv(comments=comments), exc=EXC)
        self.assertEqual(rc, 0, out)                                   # control: everything independent -> ELIGIBLE
        for gt in (None, {"status": "UNVERIFIED", "reasons": ["self-pin"]}, {"status": "verified"}, {}):
            with self.subTest(gate_trust=gt):
                rc, out = run(reviews=rv(comments=comments), exc=EXC, gate_trust=gt)
                self.assertEqual(rc, 1)
                self.assertIn("TRUSTED GATE UNVERIFIED", out)
                self.assertIn("NOT ELIGIBLE", out)


if __name__ == "__main__":
    unittest.main()
