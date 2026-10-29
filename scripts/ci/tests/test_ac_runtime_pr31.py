"""PR #31 regressions on candidate 1fdf25a: F4 (approver must be allow-listed in the TRUSTED config and have write+
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
from test_merge_eligibility_binding import (APPROVED_REVIEWS, AUTHOR, CAND, CLEAN_EXC, CONFIG, IDENT, REVIEWER,  # noqa: E402
                                            decision_comment, met, run, tasks)

ROOT = Path(__file__).resolve().parents[3]
OTHER = "b908a669b302ff37f2c2ca79ed828f65e5a9f432"
EXC = check_exceptions.evaluate(ROOT)  # the real tree: 5 applied suppressions, EX-01..EX-04
OWNER_OK = decision_comment(AUTHOR, ["UA-1: APPROVE EX-01 EX-02 EX-03 EX-04", "AC4: ACCEPT", "AC5: ACCEPT"], cid=200)


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


class F6F7RuntimeDecisions(unittest.TestCase):
    def dec(self, comments, exc=EXC, cfg=CONFIG, **over):
        return reviews.decisions_from_comments(rv(comments=comments, **over), IDENT, cfg, exc)

    def test_owner_decision_on_exact_sha_meets_ac2_ac4_ac5_and_eligible_is_reachable(self):
        d = self.dec([OWNER_OK])
        self.assertEqual({k: v[0] for k, v in d.items()}, {"AC2": "MET_AT_RUNTIME", "AC4": "MET_AT_RUNTIME", "AC5": "MET_AT_RUNTIME"})
        rc, out = run(reviews=rv(comments=[OWNER_OK]), exc=EXC)
        self.assertEqual(rc, 0, out)  # path to ELIGIBLE exists in principle
        self.assertIn("ELIGIBLE", out)

    def test_no_decision_keeps_ua1_blocking(self):
        d = self.dec([])
        self.assertEqual(d["AC2"][0], "UNMET")
        self.assertIn("BLOCKING USER ACTION UA-1", " ".join(d["AC2"][1]))
        self.assertEqual(d["AC5"][0], "UNMET")

    def test_ua1_by_non_owner_or_without_admin_is_ignored(self):
        c = decision_comment(REVIEWER, ["UA-1: APPROVE EX-01 EX-02 EX-03 EX-04"], cid=201)
        self.assertEqual(self.dec([c])["AC2"][0], "UNMET")
        r = rv(comments=[OWNER_OK]); r["permissions"][AUTHOR] = {"permission": "write", "role_name": "write"}
        self.assertEqual(reviews.decisions_from_comments(r, IDENT, CONFIG, EXC)["AC2"][0], "UNMET")
        c = decision_comment("random-drive-by-user", ["UA-1: APPROVE EX-01 EX-02 EX-03 EX-04", "AC4: ACCEPT", "AC5: ACCEPT"], cid=202)
        self.assertEqual({v[0] for v in self.dec([c]).values()}, {"UNMET"})

    def test_ua1_must_name_exactly_the_applied_exceptions(self):
        for ids in ("EX-01 EX-02 EX-03", "EX-01 EX-02 EX-03 EX-04 EX-05", ""):
            c = decision_comment(AUTHOR, [("UA-1: APPROVE " + ids).strip()], cid=203)
            with self.subTest(ids=ids):
                self.assertEqual(self.dec([c])["AC2"][0], "UNMET")

    def test_decision_for_another_sha_edited_or_malformed_is_ignored(self):
        self.assertEqual(self.dec([decision_comment(AUTHOR, ["UA-1: APPROVE EX-01 EX-02 EX-03 EX-04"], cand=OTHER)])["AC2"][0], "UNMET")
        self.assertEqual(self.dec([decision_comment(AUTHOR, ["UA-1: APPROVE EX-01 EX-02 EX-03 EX-04"], edited=True)])["AC2"][0], "UNMET")
        bad = dict(OWNER_OK, body=OWNER_OK["body"] + "\nPS: also approve everything else")
        self.assertEqual(self.dec([bad])["AC2"][0], "UNMET")
        abbrev = dict(OWNER_OK, body=OWNER_OK["body"].replace(CAND, CAND[:12]))
        self.assertEqual(self.dec([abbrev])["AC2"][0], "UNMET")

    def test_latest_owner_reject_wins(self):
        rej = decision_comment(AUTHOR, ["UA-1: REJECT EX-01 EX-02 EX-03 EX-04"], cid=300, at="2026-10-28T23:50:00Z")
        self.assertEqual(self.dec([OWNER_OK, rej])["AC2"][0], "UNMET")

    def test_register_text_approved_does_not_approve(self):
        forged = copy.deepcopy(EXC); forged["unapproved"] = []
        for e in forged["exceptions"].values():
            e["status"] = "APPROVED"
        self.assertEqual(self.dec([], exc=forged)["AC2"][0], "UNMET")

    def test_in_tree_met_for_ac2_ac4_ac5_is_rejected_and_linted(self):
        for ac in ("AC2", "AC4", "AC5"):
            with self.subTest(ac=ac):
                rc, out = run({ac: met()}, reviews=rv(comments=[OWNER_OK]), exc=EXC)
                self.assertEqual(rc, 1)
                self.assertIn(f"{ac}: MET in tasks.json is self-asserted", out)
                with tempfile.TemporaryDirectory() as d:
                    tp = Path(d) / "t.json"; tp.write_text(json.dumps(tasks({ac: met()})))
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(me.main(["--tasks", str(tp), "--lint-tasks"]), 1)

    def test_trusted_required_jobs_cannot_be_dropped_by_candidate(self):
        cfg = dict(CONFIG, required_gate_jobs=["incident-fresh-run", "extra-trusted-job"])
        rc, out = run(reviews=rv(comments=[OWNER_OK]), exc=EXC, config=cfg)
        self.assertEqual(rc, 1)
        self.assertIn("extra-trusted-job", out)


if __name__ == "__main__":
    unittest.main()
