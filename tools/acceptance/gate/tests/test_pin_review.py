"""T-16 / false-acceptance regressions for the merge-eligibility trusted pin (stdlib only).

The proposed manifest in acceptance/pin-review/T-16/ was prepared by the shared agent account. It must not be able to
turn merge-eligibility green on its own: until an independent, allow-listed, write-permitted non-author approves its
gate_sha (and the owner installs it in a trusted location), main's own gate code must report TRUSTED GATE UNVERIFIED.
These tests drive main's verifier (scripts/ci/verify_trusted_gate.py, imported read-only, never modified) with that file.
"""
import copy, hashlib, importlib.util, json, subprocess, unittest
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True,
                           cwd=Path(__file__).resolve().parent).stdout.strip())
T16 = ROOT / "acceptance/pin-review/T-16"
PROPOSED = T16 / "gate-manifest.PROPOSED-NOT-TRUSTED.json"
CURRENT = T16 / "trusted-manifest.CURRENT.evidence-acceptance-750de1c6.json"
STALE = "scripts/ci/tests/test_module_coverage.py"
OLD, NEW = ("92cd251e7325b7892ccab83a9af6e81b13c58f9e2f9394b0d83d7890dda6ac9d",
            "e481f054a2d68d75122c46298a5de831dea9d09f121f364ae43ae35bae48f5e9")
SHARED_AGENT = "onnxscibroccoli"


def _vtg():
    spec = importlib.util.spec_from_file_location("vtg_main", ROOT / "scripts/ci/verify_trusted_gate.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


VTG = _vtg()
CFG = json.loads((ROOT / ".github/acceptance/trusted-config.json").read_text())


def have(sha):
    return subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", sha + "^{commit}"], capture_output=True).returncode == 0


class ProposedPinIsNotTrust(unittest.TestCase):
    def setUp(self):
        self.p = json.loads(PROPOSED.read_text()); self.c = json.loads(CURRENT.read_text())
        self.cand = "8e2df97b558e69032e52a50ed0adfd311ad04578"

    def test_t16_exactly_one_stale_entry(self):
        diff = {k for k in set(self.p["files"]) | set(self.c["files"]) if self.p["files"].get(k) != self.c["files"].get(k)}
        self.assertEqual(diff, {STALE})
        self.assertEqual((self.c["files"][STALE], self.p["files"][STALE]), (OLD, NEW))

    def test_proposed_records_no_review(self):
        self.assertIsNone(self.p.get("independent_review"))
        self.assertIn("PROPOSED, NOT TRUSTED", self.p["note"])

    def test_proposed_hashes_are_derived_from_its_gate_sha(self):
        if not have(self.p["gate_sha"]):
            self.skipTest("gate_sha not in this clone (shallow checkout)")
        self.assertEqual(VTG.build(ROOT, self.p["gate_sha"])["files"], self.p["files"])

    def test_FA_T16_1_unapproved_proposed_manifest_is_unverified(self):
        st, why = VTG.pin_trust(self.p, self.cand, CFG, None, None, None)
        self.assertEqual(st, "UNVERIFIED")
        self.assertTrue(any("no independently reviewed gate pin" in w for w in why), why)

    def test_FA_T16_2_runtime_trust_unverified_even_when_hashes_bind(self):
        if not have(self.p["gate_sha"]):
            self.skipTest("gate_sha not in this clone (shallow checkout)")
        # A run whose trusted checkout, executing scripts/ci and workflow all match the proposed pin still fails D3.
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            wt = Path(td) / "gate"
            # a throwaway shared clone, so the repository under test is not modified
            subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(wt)], check=True)
            subprocess.run(["git", "-C", str(wt), "checkout", "-q", "--detach", self.p["gate_sha"]], check=True)
            res = VTG.gate_trust_at_runtime(self.p, self.cand, wt, wt / "scripts/ci", wt / VTG.CONFIG, ROOT, self.cand)
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertEqual([w for w in res["reasons"] if "no independently reviewed" not in w], [], res["reasons"])

    def _forged(self, login, author, perm="admin", allow=None):
        m = copy.deepcopy(self.p); m["independent_review"] = {"pr": 40, "review_id": 1}
        cfg = dict(CFG); cfg["reviewer_allowlist"] = allow if allow is not None else CFG.get("reviewer_allowlist", [])
        r = {"id": 1, "state": "APPROVED", "commit_id": m["gate_sha"], "user": {"login": login}}
        return VTG.pin_trust(m, self.cand, cfg, r, author, perm)

    def test_FA_T16_3_shared_agent_self_approval_rejected(self):
        st, why = self._forged(SHARED_AGENT, SHARED_AGENT)
        self.assertEqual(st, "UNVERIFIED"); self.assertTrue(any("PR author" in w for w in why), why)
        st, why = self._forged(SHARED_AGENT, SHARED_AGENT, allow=[SHARED_AGENT])
        self.assertEqual(st, "UNVERIFIED"); self.assertTrue(any("PR author" in w for w in why), why)

    def test_FA_T16_4_reviewer_not_allowlisted_rejected(self):
        self.assertEqual(CFG.get("reviewer_allowlist"), [], "allowlist changed: update T-16 blockers")
        st, why = self._forged("some-human", SHARED_AGENT)
        self.assertEqual(st, "UNVERIFIED"); self.assertTrue(any("allowlist" in w for w in why), why)

    def test_FA_T16_5_read_only_reviewer_rejected(self):
        st, why = self._forged("some-human", SHARED_AGENT, perm="read", allow=["some-human"])
        self.assertEqual(st, "UNVERIFIED"); self.assertTrue(any("permission" in w for w in why), why)

    def test_FA_T16_6_self_pin_rejected(self):
        st, why = VTG.pin_trust(self.p, self.p["gate_sha"], CFG, None, None, None)
        self.assertTrue(any("self-pin" in w for w in why), why)

    def test_control_only_a_qualifying_review_verifies(self):
        # The pure rule CAN verify, so the UNVERIFIED results above are not vacuous.
        st, why = self._forged("independent-human", SHARED_AGENT, perm="write", allow=["independent-human"])
        self.assertEqual((st, why), ("VERIFIED", []))

    def test_FA_T16_7_proposed_manifest_not_installed_in_a_trusted_location(self):
        installed = ROOT / ".github/acceptance/gate-manifest.json"
        if installed.exists():
            self.assertNotEqual(hashlib.sha256(installed.read_bytes()).digest(), hashlib.sha256(PROPOSED.read_bytes()).digest())
            self.assertIsNotNone(json.loads(installed.read_text()).get("independent_review"))

    def test_evidence_package_hashes(self):
        lines = (T16 / "SHA256SUMS").read_text().splitlines()
        self.assertTrue(lines)
        for l in lines:
            h, name = l.split("  ", 1)
            self.assertEqual(hashlib.sha256((T16 / name).read_bytes()).hexdigest(), h, name)


if __name__ == "__main__":
    unittest.main()
