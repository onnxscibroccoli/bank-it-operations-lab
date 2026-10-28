"""SIMULATION - offline contract tests: fixtures and mock responses vs contract/openapi.json."""
import json
import unittest

from tests import _offline  # noqa: F401  (blocks network, sets sys.path)
from vendor_mock.contract import ContractError, load_contract, validate, validate_response
from vendor_mock.mock import FIXTURES, SCENARIOS, AcmeLedgerMock

C = load_contract()
S = C["components"]["schemas"]
JSON_SIM = {"Content-Type": "application/json", "X-Simulation": "SIMULATION"}
LAB = (b"grant_type=client_credentials&client_id=SIMULATION-client-lab"
       b"&client_secret=SIMULATION-secret-not-real")


def acct():
    return json.loads((FIXTURES / "accounts.json").read_text())["accounts"][0]


class ContractDocument(unittest.TestCase):
    def test_contract_is_labelled_simulation_and_disclaims_compatibility(self):
        info = C["info"]
        self.assertIn("SIMULATION", info["title"])
        self.assertTrue(info["x-simulation"])
        self.assertIn("No authoritative compatibility evidence exists", info["description"])
        self.assertTrue(all(s["url"].endswith(".invalid") for s in C["servers"]))

    def test_every_declared_response_has_a_schema_and_all_refs_resolve(self):
        for path, ops in C["paths"].items():
            for method, op in ops.items():
                for status, resp in op["responses"].items():
                    sch = resp["content"]["application/json"]["schema"]
                    self.assertIn(sch["$ref"].rsplit("/", 1)[1], S, f"{method} {path} {status}")
                    if status == "429":
                        self.assertIn("Retry-After", resp["headers"])


class Fixtures(unittest.TestCase):
    def test_fixture_files_are_labelled_simulation(self):
        for f in FIXTURES.glob("*.json"):
            self.assertTrue(json.loads(f.read_text())["_simulation_notice"].startswith("SIMULATION"), f)

    def test_account_fixtures_match_schema(self):
        for a in json.loads((FIXTURES / "accounts.json").read_text())["accounts"]:
            validate(C, S["Account"], a)

    def test_transaction_fixtures_match_schema(self):
        for txns in json.loads((FIXTURES / "transactions.json").read_text())["transactions"].values():
            for t in txns:
                validate(C, S["Transaction"], t)
                self.assertTrue(t["description"].startswith("SIMULATION "))


class MockResponsesMatchContract(unittest.TestCase):
    def _token(self, m, body=LAB):
        r = m.handle("POST", "/oauth/token", {}, body, 1.0)
        return validate_response(C, "POST", "/oauth/token", r.status, r.headers, r.body)["access_token"]

    def test_normal_responses_valid(self):
        m = AcmeLedgerMock()
        h = {"Authorization": f"Bearer {self._token(m)}"}
        for method, path, status in [
            ("GET", "/v1/health", 200),
            ("GET", "/v1/accounts/SIM-ACCT-000101", 200),
            ("GET", "/v1/accounts/SIM-ACCT-000202", 200),
            ("GET", "/v1/accounts/SIM-ACCT-000101/transactions?limit=2", 200),
            ("GET", "/v1/accounts/SIM-ACCT-000202/transactions", 200),
            ("GET", "/v1/accounts/SIM-ACCT-999999", 404),
            ("GET", "/v1/accounts/SIM-ACCT-999999/transactions", 404),
        ]:
            with self.subTest(path=path):
                r = m.handle(method, path, h, b"", 1.0)
                self.assertEqual(r.status, status)
                body = validate_response(C, method, path, r.status, r.headers, r.body)
                self.assertEqual(body["simulation"], "SIMULATION")

    def test_error_responses_valid(self):
        m = AcmeLedgerMock()
        p = "/v1/accounts/SIM-ACCT-000101"
        r = m.handle("GET", p, {}, b"", 1.0)  # no token
        self.assertEqual(validate_response(C, "GET", p, r.status, r.headers, r.body)["error"], "invalid_token")
        r = m.handle("POST", "/oauth/token", {}, b"client_id=x&client_secret=y&grant_type=client_credentials", 1.0)
        self.assertEqual(validate_response(C, "POST", "/oauth/token", r.status, r.headers, r.body)["error"],
                         "invalid_client")

    def test_insufficient_scope_is_403(self):
        m = AcmeLedgerMock()
        tok = self._token(m, LAB.replace(b"client-lab", b"client-noscope"))
        r = m.handle("GET", "/v1/accounts/SIM-ACCT-000101", {"Authorization": f"Bearer {tok}"}, b"", 1.0)
        self.assertEqual(r.status, 403)
        validate_response(C, "GET", "/v1/accounts/SIM-ACCT-000101", 403, r.headers, r.body)

    def test_rate_limit_responses_carry_valid_retry_after(self):
        r = AcmeLedgerMock("rate_limit_always").handle("GET", "/v1/accounts/SIM-ACCT-000101", {}, b"", 1.0)
        self.assertEqual(r.status, 429)
        validate_response(C, "GET", "/v1/accounts/SIM-ACCT-000101", 429, r.headers, r.body)

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):
            AcmeLedgerMock("not-a-scenario")
        self.assertIn("normal", SCENARIOS)


class ValidatorNegatives(unittest.TestCase):
    """The validator must reject each class of contract violation (no false PASS)."""

    def bad(self, schema, value):
        with self.assertRaises(ContractError):
            validate(C, schema, value)

    def test_missing_required(self):
        a = acct(); del a["status"]; self.bad(S["Account"], a)

    def test_additional_property(self):
        a = acct(); a["ssn"] = "x"; self.bad(S["Account"], a)

    def test_wrong_type(self):
        a = acct(); a["available_balance"] = "100"; self.bad(S["Account"], a)

    def test_bool_is_not_integer(self):
        a = acct(); a["ledger_balance"]["amount_minor"] = True; self.bad(S["Account"], a)

    def test_float_is_not_integer(self):
        a = acct(); a["ledger_balance"]["amount_minor"] = 1.5; self.bad(S["Account"], a)

    def test_enum(self):
        a = acct(); a["status"] = "open"; self.bad(S["Account"], a)

    def test_pattern_unmasked_account_number(self):
        a = acct(); a["masked_number"] = "123456780101"; self.bad(S["Account"], a)

    def test_simulation_label_required(self):
        a = acct(); a["simulation"] = "PRODUCTION"; self.bad(S["Account"], a)

    def test_bad_datetime(self):
        a = acct(); a["as_of"] = "2026-13-45T99:00:00Z"; self.bad(S["Account"], a)
        a["as_of"] = "yesterday"; self.bad(S["Account"], a)

    def test_token_bounds(self):
        self.bad(S["Token"], {"simulation": "SIMULATION", "access_token": "SIMULATION-tok-abcdefgh",
                              "token_type": "Bearer", "expires_in": 0, "scope": ""})

    def test_raw_response_negatives(self):
        p = "/v1/accounts/SIM-ACCT-000101"
        good = json.dumps(acct()).encode()
        nan = good.replace(b'"simulation": "SIMULATION"', b'"simulation": "SIMULATION", "x": NaN')
        cases = {
            "undeclared status": (418, JSON_SIM, good),
            "missing X-Simulation": (200, {"Content-Type": "application/json"}, good),
            "wrong content-type": (200, {**JSON_SIM, "Content-Type": "text/html"}, good),
            "truncated json": (200, JSON_SIM, good[:20]),
            "non-utf8": (200, JSON_SIM, b"\xff" + good),
            "NaN": (200, JSON_SIM, nan),
            "429 missing Retry-After": (429, JSON_SIM, b"{}"),
            "429 http-date Retry-After": (429, {**JSON_SIM, "Retry-After": "Wed, 28 Oct 2026 12:00:00 GMT"}, b"{}"),
            "429 Retry-After too large": (429, {**JSON_SIM, "Retry-After": "86400"}, b"{}"),
        }
        self.assertNotEqual(nan, good)
        for name, (status, headers, body) in cases.items():
            with self.subTest(name):
                with self.assertRaises(ContractError):
                    validate_response(C, "GET", p, status, headers, body)

    def test_unknown_path_and_method(self):
        with self.assertRaises(ContractError):
            validate_response(C, "GET", "/v2/anything", 200, JSON_SIM, b"{}")
        with self.assertRaises(ContractError):
            validate_response(C, "DELETE", "/v1/health", 200, JSON_SIM, b"{}")


if __name__ == "__main__":
    unittest.main()
