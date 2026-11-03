"""T-16 (candidate-20261103b): a new gate pin is prepared UNREVIEWED and can never make the gate trusted by itself;
merge-eligibility stays fail-closed on pushes to main and whenever independent approval is missing."""
import copy, json, subprocess, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_trusted_gate as vtg  # noqa: E402
from test_merge_eligibility_binding import APPROVED_REVIEWS, AUTHOR, CAND, IDENT, REVIEWER, run  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
PROPOSAL = ROOT / "coordination/proposed-gate-pin/gate-manifest.json"
REAL_CONFIG = json.loads((ROOT / ".github/acceptance/trusted-config.json").read_text())
HEAD = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
OTHER = "1" * 40


def approving(login, commit):
    return {"id": 9, "user": {"login": login}, "state": "APPROVED", "commit_id": commit}


class ProposedPinStaysUnreviewed(unittest.TestCase):
    def manifests(self):
        built = vtg.build(ROOT, HEAD) if HEAD else {"gate_sha": OTHER, "files": {}}
        built["independent_review"] = None
        out = [built]
        if PROPOSAL.exists():
            out.append(json.loads(PROPOSAL.read_text()))
        return out

    def test_committed_proposal_records_no_review_and_no_trust_marker(self):
        if not PROPOSAL.exists():
            self.skipTest("no committed pin proposal at this commit")
        man = json.loads(PROPOSAL.read_text())
        self.assertIsNone(man.get("independent_review"))
        self.assertEqual(man.get("review_status"), "UNREVIEWED")
        self.assertFalse({k for k in man if k.lower() in ("trusted", "verified", "status")} - {"review_status"})

    def test_unreviewed_pin_is_unverified(self):
        for man in self.manifests():
            with self.subTest(gate=man.get("gate_sha")):
                st, why = vtg.pin_trust(man, OTHER, REAL_CONFIG, None, None, None)
                self.assertEqual(st, "UNVERIFIED")
                self.assertIn("no independently reviewed gate pin", " ".join(why))

    def test_forged_review_record_does_not_make_it_trusted(self):
        # Writing {pr, review_id} into the manifest is not enough: the live allow-list is empty and the shared
        # account is the PR author, so neither its approval nor an unlisted account's approval counts.
        for man in self.manifests():
            forged = dict(man, independent_review={"pr": 42, "review_id": 1})
            g = forged["gate_sha"]
            for login, perm in ((AUTHOR, "admin"), ("someone-else", "write")):
                with self.subTest(gate=g, login=login):
                    st, _ = vtg.pin_trust(forged, OTHER, REAL_CONFIG, approving(login, g), AUTHOR, perm)
                    self.assertEqual(st, "UNVERIFIED")

    def test_self_pin_of_the_candidate_is_unverified(self):
        for man in self.manifests():
            st, why = vtg.pin_trust(man, man["gate_sha"], REAL_CONFIG, None, None, None)
            self.assertEqual(st, "UNVERIFIED")
            self.assertIn("self-pin", " ".join(why))


class MergeEligibilityFailClosed(unittest.TestCase):
    def test_push_to_main_is_a_direct_run_and_not_eligible(self):
        direct = dict(IDENT, kind="direct", event="push", base_sha=None)
        rc, out = run(ident=direct)
        self.assertEqual(rc, 1)
        self.assertIn("NOT ELIGIBLE", out)
        self.assertIn("direct run", out)

    def test_missing_independent_approval_is_not_eligible(self):
        for reviews in ({**APPROVED_REVIEWS, "reviews": []},
                        {**APPROVED_REVIEWS, "reviews": [approving(AUTHOR, CAND)]},
                        {**APPROVED_REVIEWS, "reviews": [dict(approving(REVIEWER, CAND), state="COMMENTED")]},
                        None):
            with self.subTest(reviews=None if reviews is None else reviews["reviews"]):
                rc, out = run(reviews=reviews)
                self.assertEqual(rc, 1)
                self.assertIn("NOT ELIGIBLE", out)

    def test_unverified_gate_trust_is_not_eligible(self):
        rc, out = run(gate_trust={"status": "UNVERIFIED", "reasons": ["no independently reviewed gate pin"]})
        self.assertEqual(rc, 1)
        self.assertIn("TRUSTED GATE UNVERIFIED", out)


if __name__ == "__main__":
    unittest.main()
