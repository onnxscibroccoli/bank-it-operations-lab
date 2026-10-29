"""Regressions for the PR #30 findings on candidate b908a66: F3/R6 (AC1 from the reviews API, never self-asserted),
B5-1 (applied suppressions tied to non-APPROVED exceptions block AC2/AC5), and the trusted-gate data root."""
import copy, io, json, shutil, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_exceptions, reviews  # noqa: E402
import merge_eligibility as me  # noqa: E402
from test_merge_eligibility_binding import APPROVED_REVIEWS, AUTHOR, CAND, CLEAN_EXC, CONFIG, IDENT, REVIEWER, decision_comment, run, met  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OTHER = "b908a669b302ff37f2c2ca79ed828f65e5a9f432"


def rv(*reviews_, **over):
    r = copy.deepcopy(APPROVED_REVIEWS); r["reviews"] = list(reviews_); r.update(over); return r


def review(login, state, commit=CAND, at="2026-10-28T23:00:00Z", rid=1):
    return {"id": rid, "user": {"login": login}, "state": state, "commit_id": commit, "submitted_at": at}


class AC1FromReviews(unittest.TestCase):
    def test_control_independent_approval_on_exact_sha(self):
        rc, out = run()
        self.assertEqual(rc, 0, out)
        self.assertIn("AC1: MET_AT_RUNTIME", out)

    def test_same_account_approval_never_counts(self):
        st, why = reviews.ac1_from_reviews(rv(review(AUTHOR, "APPROVED")), IDENT, CONFIG)
        self.assertEqual(st, "UNMET")
        self.assertIn("same-account", " ".join(why))
        st, _ = reviews.ac1_from_reviews(rv(review(AUTHOR.upper(), "APPROVED")), IDENT, CONFIG)
        self.assertEqual(st, "UNMET")

    def test_approval_of_another_commit_does_not_count(self):
        st, _ = reviews.ac1_from_reviews(rv(review("rev", "APPROVED", commit=OTHER)), IDENT, CONFIG)
        self.assertEqual(st, "UNMET")
        st, _ = reviews.ac1_from_reviews(rv(review("rev", "APPROVED", commit=CAND[:7])), IDENT, CONFIG)
        self.assertEqual(st, "UNMET")

    def test_pr_head_moved_past_candidate(self):
        st, why = reviews.ac1_from_reviews(rv(review("rev", "APPROVED"), head_sha=OTHER), IDENT, CONFIG)
        self.assertEqual(st, "UNMET")
        self.assertIn("is not the candidate", " ".join(why))

    def test_commented_only_or_dismissed_or_later_changes_requested(self):
        self.assertEqual(reviews.ac1_from_reviews(rv(review("rev", "COMMENTED")), IDENT, CONFIG)[0], "UNMET")
        self.assertEqual(reviews.ac1_from_reviews(rv(review("rev", "APPROVED", rid=1), review("rev", "DISMISSED", at="2026-10-28T23:30:00Z", rid=2)), IDENT, CONFIG)[0], "UNMET")
        self.assertEqual(reviews.ac1_from_reviews(rv(review("rev", "APPROVED", rid=1), review("rev2", "CHANGES_REQUESTED", rid=2)), IDENT, CONFIG)[0], "UNMET")
        # a later approval by the same reviewer supersedes its earlier changes-requested
        self.assertEqual(reviews.ac1_from_reviews(rv(review(REVIEWER, "CHANGES_REQUESTED", rid=1), review(REVIEWER, "APPROVED", at="2026-10-28T23:30:00Z", rid=2)), IDENT, CONFIG)[0], "MET_AT_RUNTIME")

    def test_fetch_failure_or_missing_reviews_fails_closed(self):
        self.assertEqual(reviews.ac1_from_reviews({"ok": False, "error": "HTTPError 403"}, IDENT, CONFIG)[0], "UNMET")
        rc, out = run(reviews=None)
        self.assertEqual(rc, 1)
        self.assertIn("reviews not fetched", out)

    def test_ac1_met_in_tasks_is_rejected_even_when_bound(self):
        rc, out = run({"AC1": met()})
        self.assertEqual(rc, 1)
        self.assertIn("self-asserted", out)
        with tempfile.TemporaryDirectory() as d:
            from test_merge_eligibility_binding import tasks
            tp = Path(d) / "t.json"; tp.write_text(json.dumps(tasks({"AC1": met()})))
            with redirect_stdout(io.StringIO()) as o:
                self.assertEqual(me.main(["--tasks", str(tp), "--lint-tasks"]), 1)
            self.assertIn("AC1: MET in tasks.json is not accepted", o.getvalue())


class SecurityExceptionsGate(unittest.TestCase):
    def test_repo_suppressions_are_registered_but_unapproved(self):
        r = check_exceptions.evaluate(ROOT)
        self.assertEqual(r["errors"], [])
        self.assertEqual(len(r["applied"]), 5)
        self.assertEqual(sorted({u["exception"] for u in r["unapproved"]}), ["EX-01", "EX-02", "EX-03", "EX-04"])
        self.assertTrue(r["blocking_user_action"])

    def test_unapproved_exceptions_keep_ac2_ac5_unmet_even_if_tasks_say_met(self):
        r = check_exceptions.evaluate(ROOT)
        rc, out = run(exc=r)
        self.assertEqual(rc, 1)
        self.assertIn("AC2: UNMET", out)
        self.assertIn("AC5: UNMET", out)
        self.assertIn("BLOCKING USER ACTION UA-1", out)

    def _tree(self, d, register_edit=None, template_edit=None):
        ev = "evidence/aws/aws-remediation-vpc-rds"
        shutil.copytree(ROOT / ev / "synth", Path(d) / ev / "synth")
        reg = (ROOT / ev / "SECURITY_EXCEPTIONS.md").read_text()
        (Path(d) / ev / "SECURITY_EXCEPTIONS.md").write_text(register_edit(reg) if register_edit else reg)
        if template_edit:
            p = Path(d) / ev / "synth/BankItLabSecureStorage.template.json"
            p.write_text(json.dumps(template_edit(json.loads(p.read_text()))))
        return d

    def test_all_approved_unblocks(self):
        with tempfile.TemporaryDirectory() as d:
            self._tree(d, lambda s: s.replace("**PROPOSED, pending owner approval.**", "**APPROVED by owner (test fixture).**"))
            r = check_exceptions.evaluate(d)
            self.assertEqual((r["errors"], r["unapproved"], r["blocking_user_action"]), ([], [], False))

    def test_one_entry_still_proposed_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            self._tree(d, lambda s: s.replace("**PROPOSED, pending owner approval.**", "**APPROVED**") + "\nEX-03 status: PROPOSED\n")
            r = check_exceptions.evaluate(d)
            self.assertEqual([u["exception"] for u in r["unapproved"]], ["EX-03"])

    def test_unregistered_or_mismatched_suppression_is_an_error(self):
        def add(t, reason, rule):
            res = next(iter(t["Resources"].values()))
            res.setdefault("Metadata", {}).setdefault("cdk_nag", {}).setdefault("rules_to_suppress", []).append({"id": rule, "reason": reason})
            return t
        for reason, rule, msg in (("no exception id", "AwsSolutions-S1", "names no registered exception"),
                                  ("EX-09: not registered", "AwsSolutions-S1", "not in the register"),
                                  ("EX-01: wrong rule", "AwsSolutions-S1", "registers rule")):
            with self.subTest(msg=msg), tempfile.TemporaryDirectory() as d:
                self._tree(d, template_edit=lambda t: add(t, reason, rule))
                r = check_exceptions.evaluate(d)
                self.assertTrue(any(msg in e for e in r["errors"]), r["errors"])
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(check_exceptions.main(["--root", d]), 1)

    def test_missing_register_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            r = check_exceptions.evaluate(d)
            self.assertTrue(r["blocking_user_action"])
            rc, out = run(exc=r)
            self.assertEqual(rc, 1)

    def test_strict_mode_exits_3_when_blocking(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check_exceptions.main(["--strict"]), 3)
            self.assertEqual(check_exceptions.main([]), 0)


class TrustedGateDataRoot(unittest.TestCase):
    def test_data_root_is_evaluated_not_the_gate_copy(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "coordination").mkdir()
            t = json.loads((ROOT / "coordination/tasks.json").read_text())
            (Path(d) / "coordination/tasks.json").write_text(json.dumps(t))
            reg = json.loads((ROOT / "coordination/modules.json").read_text()); reg["required_gate_jobs"] = []
            (Path(d) / "coordination/modules.json").write_text(json.dumps(reg))
            with redirect_stdout(io.StringIO()) as out:
                rc = me.main(["--root", d])
            self.assertEqual(rc, 1)
            self.assertIn("required_gate_jobs missing", out.getvalue())


if __name__ == "__main__":
    unittest.main()
