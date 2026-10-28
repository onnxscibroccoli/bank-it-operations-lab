"""Fixture tests for operations/hardening/tools/score_units.py (stdlib unittest; pytest-compatible).

Run from the repo root:
  python3 -m unittest discover -s operations/hardening/tests -v
  python3 -m pytest operations/hardening/tests
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
HARD = os.path.join(HERE, "..")
TOOL = os.path.join(HARD, "tools", "score_units.py")
UNITS = os.path.join(HARD, "systemd", "units")
DROPINS = os.path.join(HARD, "systemd", "dropins")
sys.path.insert(0, os.path.join(HARD, "tools"))
import score_units as su  # noqa: E402


def cases():
    with open(os.path.join(FIX, "INDEX.json"), encoding="utf-8") as fh:
        return json.load(fh)["cases"]


def d(name):
    return os.path.join(DROPINS, name)


class FixtureCases(unittest.TestCase):
    def test_cli_exit_codes(self):
        for c in cases():
            with self.subTest(case=c["id"]):
                r = subprocess.run([sys.executable, TOOL] + c["args"] + ["--json"], cwd=FIX,
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, c["expectedExit"], r.stdout[-1200:] + r.stderr)
                json.loads(r.stdout)

    def test_every_fixture_file_is_used(self):
        used = {a for c in cases() for a in c["args"] if "." in a and not a[0].isdigit()}
        on_disk = set(os.listdir(FIX)) - {"INDEX.json"}
        self.assertEqual(on_disk - used, set())


class Semantics(unittest.TestCase):
    def test_empty_bounding_set_means_no_caps(self):
        self.assertEqual(su.cap_state([""], "t"), set())

    def test_tilde_alone_resets_to_full(self):
        self.assertEqual(su.cap_state(["", "~"], "t"), su.ALL_CAPS)

    def test_allow_lists_or_together(self):
        self.assertEqual(su.cap_state(["CAP_CHOWN", "CAP_KILL"], "t"), {"CAP_CHOWN", "CAP_KILL"})

    def test_deny_list_removes(self):
        st = su.cap_state(["~CAP_SYS_ADMIN"], "t")
        self.assertNotIn("CAP_SYS_ADMIN", st)
        self.assertIn("CAP_CHOWN", st)

    def test_empty_scalar_resets(self):
        s, _, _ = su.merge(os.path.join(FIX, "base-for-dropins.service"),
                           [os.path.join(FIX, "dropin-10-strong.conf"), os.path.join(FIX, "dropin-90-weaken.conf")])
        self.assertNotIn("ProtectSystem", s)

    def test_dropins_applied_in_filename_order(self):
        a = su.score(os.path.join(FIX, "base-for-dropins.service"),
                     [os.path.join(FIX, "dropin-90-weaken.conf"), os.path.join(FIX, "dropin-10-strong.conf")])
        b = su.score(os.path.join(FIX, "base-for-dropins.service"),
                     [os.path.join(FIX, "dropin-10-strong.conf"), os.path.join(FIX, "dropin-90-weaken.conf")])
        self.assertEqual(a["declaredExposure"], b["declaredExposure"])
        self.assertEqual(a["dropins"], ["dropin-10-strong.conf", "dropin-90-weaken.conf"])

    def test_unsupported_value_level(self):
        rep = su.score(os.path.join(FIX, "valid-hardened-inline.service"), [], target=231)
        bad = {(u["directive"], u["value"]) for u in rep["unsupported"]}
        self.assertIn(("ProtectSystem", "strict"), bad)
        self.assertIn(("SystemCallFilter", "@system-service"), bad)
        self.assertGreater(rep["effectiveExposure"], rep["declaredExposure"])


class ShippedExamples(unittest.TestCase):
    APP = os.path.join(UNITS, "bank-lab-app.service")

    def test_unhardened_app_is_exposed(self):
        self.assertEqual(su.score(self.APP)["rating"], "EXPOSED")

    def test_layering_monotonically_improves(self):
        e0 = su.score(self.APP)["declaredExposure"]
        e1 = su.score(self.APP, [d("10-hardening-baseline.conf")])["declaredExposure"]
        e2 = su.score(self.APP, [d("10-hardening-baseline.conf"), d("20-hardening-strict.conf")])["declaredExposure"]
        self.assertLess(e1, e0)
        self.assertLess(e2, e1)

    def test_strict_stack_passes_on_modern_targets(self):
        stack = [d("10-hardening-baseline.conf"), d("20-hardening-strict.conf"), d("30-net-bind-service.conf")]
        for distro in ("rhel9", "debian12", "al2023", "ubuntu2404", "debian13", "rhel10"):
            with self.subTest(distro=distro):
                target = next(x["systemd"] for x in su.load_compat()["distros"] if x["id"] == distro)
                rep = su.score(self.APP, stack, target=target)
                self.assertEqual(rep["overall"], "PASS", rep["findings"])

    def test_strict_stack_flags_rhel8_gaps(self):
        rep = su.score(self.APP, [d("10-hardening-baseline.conf"), d("20-hardening-strict.conf")], target=239)
        names = {u["directive"] for u in rep["unsupported"]}
        self.assertTrue({"ProtectProc", "ProcSubset", "RestrictSUIDSGID", "ProtectHostname"} <= names, names)

    def test_legacy_dropin_fully_supported_on_219(self):
        rep = su.score(self.APP, [d("05-hardening-legacy-219.conf")], target=219)
        self.assertEqual(rep["unsupported"], [])

    def test_baseline_header_claims_are_true(self):
        # 10-hardening-baseline.conf says it needs systemd >= 242.
        self.assertEqual(su.score(self.APP, [d("10-hardening-baseline.conf")], target=242)["unsupported"], [])
        self.assertNotEqual(su.score(self.APP, [d("10-hardening-baseline.conf")], target=241)["unsupported"], [])

    def test_strict_header_claims_are_true(self):
        stack = [d("10-hardening-baseline.conf"), d("20-hardening-strict.conf")]
        self.assertEqual(su.score(self.APP, stack, target=247)["unsupported"], [])
        self.assertNotEqual(su.score(self.APP, stack, target=246)["unsupported"], [])

    def test_compatibility_md_matches_compat_json(self):
        with open(os.path.join(HARD, "COMPATIBILITY.md"), encoding="utf-8") as fh:
            md = fh.read()
        self.assertIn(su.render_matrix(su.load_compat()), md)


class NoSideEffects(unittest.TestCase):
    def test_tool_never_touches_the_host(self):
        with open(TOOL, encoding="utf-8") as fh:
            src = fh.read()
        for needle in ("subprocess", "systemctl", "daemon-reload", "os.system", "shutil", "open(path, \"w"):
            self.assertNotIn(needle, src, needle)


if __name__ == "__main__":
    unittest.main()
