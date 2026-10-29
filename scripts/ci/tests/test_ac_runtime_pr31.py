"""Ian 9:41/9:50 PM P1-P3 and PR #31 regressions: P1 approver authority (unauthorized, author, dismissed, superseded,
wrong/abbreviated SHA, outstanding CHANGES_REQUESTED); P2 external ACCEPTANCE-ATTESTATION v2 records bound to
candidate/main/tested merge/workflow run (forged in-tree MET never counts; a valid attestation satisfies without a
candidate commit); P3 exception states PROPOSED/APPROVED/REJECTED/APPROVED_WITH_CONDITIONS/SUPERSEDED.
Earlier PR #31 notes on candidate 1fdf25a: F4 (approver must be allow-listed in the TRUSTED config and have write+
permission; a random account approving never counts), F5 (undismissed CHANGES_REQUESTED on an earlier commit still
blocks), F6 (AC2/AC4/AC5 only from authenticated runtime decisions bound to the exact SHA; in-tree MET never counts),
F7 (UA-1 exception approval only from the trusted owner login with admin permission, naming exactly the applied IDs)."""
import copy, io, json, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_exceptions, reviews  # noqa: E402
import merge_eligibility as me  # noqa: E402
from test_merge_eligibility_binding import (APPROVED_REVIEWS, AUTHOR, BASE, CAND, CLEAN_EXC, CONFIG, IDENT, MERGE, REVIEWER,  # noqa: E402
                                            attestation, decision_comment, met, run, tasks)

ROOT = Path(__file__).resolve().parents[3]
OTHER = "b908a669b302ff37f2c2ca79ed828f65e5a9f432"
EXC = check_exceptions.evaluate(ROOT)  # the real tree: 5 applied suppressions, EX-01..EX-04
SCOPES = reviews.exception_scopes(EXC)


def exc_att(ex, decision="APPROVED", login=AUTHOR, cid=None, at="2026-10-28T23:20:00Z", scope=None, extra=(), **kw):
    return attestation(login, "EXCEPTION", decision, cid=cid or 200 + int(ex[-2:]), at=at,
                       extra=(f"exception: {ex}", f"scope: {scope or SCOPES[ex]}", *extra), **kw)


OWNER_OK = [exc_att(ex) for ex in sorted(SCOPES)]


def rv(**over):
    r = copy.deepcopy(APPROVED_REVIEWS); r.update(over); return r


def rev(login, state="APPROVED", commit=CAND, rid=9, at="2026-10-28T23:00:00Z"):
    return {"id": rid, "user": {"login": login}, "state": state, "commit_id": commit, "submitted_at": at}


class F4ApproverAuthority(unittest.TestCase):
    def test_random_account_approving_never_counts(self):
        r = rv(reviews=[rev("random-drive-by-user")])
        st, why = reviews.ac1_from_reviews(r, IDENT, CONFIG)
        self.assertEqual(st, "UNMET")
        self.assertIn("not on the trusted reviewer_allowlist", " ".join(why))
        # even with write permission on record, an account that is not allow-listed does not count
        r["permissions"]["random-drive-by-user"] = {"permission": "write", "role_name": "write"}
        self.assertEqual(reviews.ac1_from_reviews(r, IDENT, CONFIG)[0], "UNMET")

    def test_allow_listed_but_without_write_permission_never_counts(self):
        for perm in ({"permission": "read", "role_name": "read"}, {"permission": "none", "role_name": None, "error": "HTTP 404"}, None):
            r = rv()
            if perm is None:
                r["permissions"].pop(REVIEWER)
            else:
                r["permissions"][REVIEWER] = perm
            with self.subTest(perm=perm):
                st, why = reviews.ac1_from_reviews(r, IDENT, CONFIG)
                self.assertEqual(st, "UNMET")
                self.assertIn("lacks", " ".join(why))

    def test_author_on_the_allow_list_still_never_counts(self):
        cfg = dict(CONFIG, reviewer_allowlist=[AUTHOR.upper()])
        r = rv(reviews=[rev(AUTHOR)])
        self.assertEqual(reviews.ac1_from_reviews(r, IDENT, cfg)[0], "UNMET")

    def test_no_trusted_config_or_empty_allowlist_fails_closed(self):
        self.assertEqual(reviews.ac1_from_reviews(rv(), IDENT, None)[0], "UNMET")
        st, why = reviews.ac1_from_reviews(rv(), IDENT, dict(CONFIG, reviewer_allowlist=[]))
        self.assertEqual(st, "UNMET")
        self.assertIn("allowlist is empty", " ".join(why))
        rc, out = run(config=None)
        self.assertEqual(rc, 1)

    def test_control_allow_listed_write_reviewer_counts(self):
        self.assertEqual(reviews.ac1_from_reviews(rv(), IDENT, CONFIG)[0], "MET_AT_RUNTIME")

    def test_f5_changes_requested_on_earlier_commit_still_blocks(self):
        r = rv(reviews=[rev(REVIEWER, rid=1), rev("someone-else", "CHANGES_REQUESTED", commit=OTHER, rid=2, at="2026-10-28T20:00:00Z")])
        st, why = reviews.ac1_from_reviews(r, IDENT, CONFIG)
        self.assertEqual(st, "UNMET")
        self.assertIn("not dismissed", " ".join(why))


class P1ApproverAuthority(unittest.TestCase):
    def test_approval_superseded_by_later_changes_requested_from_same_reviewer(self):
        r = rv(reviews=[rev(REVIEWER, rid=1), rev(REVIEWER, "CHANGES_REQUESTED", rid=2, at="2026-10-28T23:30:00Z")])
        self.assertEqual(reviews.ac1_from_reviews(r, IDENT, CONFIG)[0], "UNMET")

    def test_dismissed_wrong_and_abbreviated_sha(self):
        for revs in ([rev(REVIEWER, rid=1), rev(REVIEWER, "DISMISSED", rid=2, at="2026-10-28T23:30:00Z")],
                     [rev(REVIEWER, commit=OTHER)], [rev(REVIEWER, commit=CAND[:12])], [rev(REVIEWER, commit=CAND.upper()[:39])]):
            with self.subTest(revs=revs):
                self.assertEqual(reviews.ac1_from_reviews(rv(reviews=revs), IDENT, CONFIG)[0], "UNMET")

    def test_author_approval(self):
        self.assertEqual(reviews.ac1_from_reviews(rv(reviews=[rev(AUTHOR)]), IDENT, dict(CONFIG, reviewer_allowlist=[AUTHOR, REVIEWER]))[0], "UNMET")


class P2ExternalAttestations(unittest.TestCase):
    def dec(self, comments, exc=EXC, cfg=CONFIG, **over):
        return reviews.decisions_from_comments(rv(comments=comments, **over), IDENT, cfg, exc)

    def test_valid_external_attestations_satisfy_without_another_candidate_commit(self):
        comments = OWNER_OK + [attestation(REVIEWER, "AC4", "ACCEPT", cid=301), attestation(REVIEWER, "AC5", "ACCEPT", cid=302)]
        d = self.dec(comments)
        self.assertEqual({k: d[k][0] for k in ("AC2", "AC4", "AC5")}, {"AC2": "MET_AT_RUNTIME", "AC4": "MET_AT_RUNTIME", "AC5": "MET_AT_RUNTIME"})
        rc, out = run(reviews=rv(comments=comments), exc=EXC)   # same tasks.json / tree: only GitHub-side records added
        self.assertEqual(rc, 0, out)
        self.assertIn(": ELIGIBLE", out)

    def test_forged_met_inside_the_candidate_is_not_eligible(self):
        forged = {ac: met() for ac in ("AC1", "AC2", "AC4", "AC5")}
        forged_exc = copy.deepcopy(EXC); forged_exc["unapproved"] = []
        for e in forged_exc["exceptions"].values():
            e["status"] = "APPROVED"
        rc, out = run(forged, reviews=rv(reviews=[], comments=[]), exc=forged_exc)
        self.assertEqual(rc, 1)
        self.assertIn("NOT ELIGIBLE", out)
        for ac in ("AC1", "AC2", "AC4", "AC5"):
            self.assertIn(f"{ac}: UNMET", out)

    def test_attestation_binding_main_tested_merge_and_run(self):
        bad = [attestation(REVIEWER, "AC4", "ACCEPT", main=OTHER),                       # wrong main
               attestation(REVIEWER, "AC4", "ACCEPT", tested=(OTHER,)),                  # other tested merge
               attestation(REVIEWER, "AC4", "ACCEPT", run="40799999999"),                # run not of this candidate
               attestation(REVIEWER, "AC4", "ACCEPT", cand=OTHER),                       # other candidate
               attestation(REVIEWER, "AC4", "ACCEPT", edited=True),                      # edited
               attestation("random-drive-by-user", "AC4", "ACCEPT"),                     # unauthorized
               decision_comment(AUTHOR, ["AC4: ACCEPT"])]                                # legacy v1 format
        for c in bad:
            with self.subTest(body=c["body"][:120]):
                self.assertEqual(self.dec([c], runs={"40800364073": {"head_sha": CAND}, "40799999999": {"head_sha": OTHER}})["AC4"][0], "UNMET")
        self.assertEqual(self.dec([attestation(REVIEWER, "AC4", "ACCEPT", tested=(OTHER, MERGE))])["AC4"][0], "MET_AT_RUNTIME")

    def test_malformed_attestations_are_ignored(self):
        good = attestation(REVIEWER, "AC4", "ACCEPT")
        for body in (good["body"] + "\nnote: extra key", good["body"].replace("candidate: " + CAND, "candidate: " + CAND[:12]),
                     good["body"].replace("decision: ACCEPT", "decision: MAYBE"), good["body"].replace("\nevidence:", "\nevidencex:")):
            with self.subTest(body=body[-60:]):
                self.assertEqual(self.dec([dict(good, body=body)])["AC4"][0], "UNMET")

    def test_latest_reject_wins_for_ac4(self):
        d = self.dec([attestation(REVIEWER, "AC4", "ACCEPT", cid=1), attestation(AUTHOR, "AC4", "REJECT", cid=2, at="2026-10-28T23:30:00Z")])
        self.assertEqual(d["AC4"][0], "UNMET")

    def test_ac5_needs_ac2(self):
        d = self.dec([attestation(REVIEWER, "AC5", "ACCEPT")])
        self.assertEqual(d["AC5"][0], "UNMET")
        self.assertIn("B5-1", " ".join(d["AC5"][1]))


class P3ExceptionStates(unittest.TestCase):
    def dec(self, comments, exc=EXC):
        return reviews.decisions_from_comments(rv(comments=comments), IDENT, CONFIG, exc)

    def test_no_decision_all_proposed_and_blocking(self):
        d = self.dec([])
        self.assertEqual(d["exceptions"], {ex: "PROPOSED" for ex in SCOPES})
        self.assertIn("BLOCKING USER ACTION UA-1", " ".join(d["AC2"][1]))

    def test_each_state(self):
        base = [exc_att(ex) for ex in ("EX-01", "EX-02", "EX-03")]
        for decision, extra, effective in (("APPROVED", (), True), ("REJECTED", (), False), ("SUPERSEDED", (), False),
                                           ("PROPOSED", (), False), ("APPROVED_WITH_CONDITIONS", ("conditions: replace with a customer-managed policy by Q1",), False)):
            with self.subTest(decision=decision):
                d = self.dec(base + [exc_att("EX-04", decision, extra=extra)])
                self.assertEqual(d["AC2"][0] == "MET_AT_RUNTIME", effective, d["AC2"][1])

    def test_conditional_approval_effective_only_after_verification(self):
        cond = exc_att("EX-04", "APPROVED_WITH_CONDITIONS", extra=("conditions: customer-managed backup policy",), at="2026-10-28T23:20:00Z")
        base = [exc_att(ex) for ex in ("EX-01", "EX-02", "EX-03")]
        self.assertEqual(self.dec(base + [cond])["AC2"][0], "UNMET")
        ver = exc_att("EX-04", "CONDITIONS_VERIFIED", login=REVIEWER, cid=299, at="2026-10-28T23:40:00Z")
        d = self.dec(base + [cond, ver])
        self.assertEqual(d["AC2"][0], "MET_AT_RUNTIME", d["AC2"][1])
        early = exc_att("EX-04", "CONDITIONS_VERIFIED", login=REVIEWER, cid=298, at="2026-10-28T23:00:00Z")   # before the approval
        self.assertEqual(self.dec(base + [early, cond])["AC2"][0], "UNMET")

    def test_scope_must_match_applied_suppressions(self):
        base = [exc_att(ex) for ex in ("EX-01", "EX-03", "EX-04")]
        narrow = exc_att("EX-02", scope=SCOPES["EX-02"].rsplit(" ", 1)[0])   # one of the two buckets only
        self.assertEqual(self.dec(base + [narrow])["AC2"][0], "UNMET")

    def test_exception_decisions_only_from_owner_with_admin(self):
        base = [exc_att(ex) for ex in ("EX-01", "EX-02", "EX-03")]
        self.assertEqual(self.dec(base + [exc_att("EX-04", login=REVIEWER)])["AC2"][0], "UNMET")
        r = rv(comments=OWNER_OK); r["permissions"][AUTHOR] = {"permission": "write", "role_name": "write"}
        self.assertEqual(reviews.decisions_from_comments(r, IDENT, CONFIG, EXC)["AC2"][0], "UNMET")

    def test_latest_owner_decision_wins(self):
        rej = exc_att("EX-01", "REJECTED", cid=400, at="2026-10-28T23:50:00Z")
        self.assertEqual(self.dec(OWNER_OK + [rej])["AC2"][0], "UNMET")

    def test_register_text_approved_does_not_approve(self):
        forged = copy.deepcopy(EXC); forged["unapproved"] = []
        for e in forged["exceptions"].values():
            e["status"] = "APPROVED"
        self.assertEqual(self.dec([], exc=forged)["AC2"][0], "UNMET")

    def test_in_tree_met_for_ac2_ac4_ac5_is_rejected_and_linted(self):
        for ac in ("AC2", "AC4", "AC5"):
            with self.subTest(ac=ac):
                rc, out = run({ac: met()}, reviews=rv(comments=OWNER_OK), exc=EXC)
                self.assertEqual(rc, 1)
                self.assertIn(f"{ac}: MET in tasks.json is self-asserted", out)
                with tempfile.TemporaryDirectory() as d:
                    tp = Path(d) / "t.json"; tp.write_text(json.dumps(tasks({ac: met()})))
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(me.main(["--tasks", str(tp), "--lint-tasks"]), 1)

    def test_trusted_required_jobs_cannot_be_dropped_by_candidate(self):
        cfg = dict(CONFIG, required_gate_jobs=["incident-fresh-run", "extra-trusted-job"])
        rc, out = run(reviews=rv(comments=OWNER_OK), exc=EXC, config=cfg)
        self.assertEqual(rc, 1)
        self.assertIn("extra-trusted-job", out)


if __name__ == "__main__":
    unittest.main()
