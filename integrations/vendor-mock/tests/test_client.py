"""SIMULATION - offline client contract tests: happy path, auth failure, timeout,
rate limiting (429 / Retry-After) and malformed responses. No network is used."""
import socket
import unittest

from tests import _offline  # (blocks network, sets sys.path)
from vendor_mock import client as vc
from vendor_mock.mock import SCENARIOS, AcmeLedgerMock, InProcessTransport

SECRET = "SIMULATION-secret-not-real"
ACCT = "SIM-ACCT-000101"


def make(scenario="normal", client_id="SIMULATION-client-lab", secret=SECRET, **kw):
    mock = AcmeLedgerMock(scenario)
    return mock, vc.AcmeLedgerClient(InProcessTransport(mock), client_id, secret, **kw)


def count(mock, prefix):
    return sum(1 for _, u in mock.calls if u.startswith(prefix))


class HappyPath(unittest.TestCase):
    def test_health(self):
        _, c = make()
        self.assertEqual(c.health(), {"simulation": "SIMULATION", "status": "OK"})

    def test_get_account(self):
        _, c = make()
        a = c.get_account(ACCT)
        self.assertEqual(a["simulation"], "SIMULATION")
        self.assertEqual(a["masked_number"], "****0101")
        self.assertEqual(a["available_balance"], {"amount_minor": 125000, "currency": "USD"})

    def test_list_transactions_paginates(self):
        m, c = make()
        txns = c.list_transactions(ACCT, limit=2)
        self.assertEqual([t["transaction_id"] for t in txns],
                         ["SIM-TXN-00000001", "SIM-TXN-00000002", "SIM-TXN-00000003"])
        self.assertEqual(sum(1 for _, u in m.calls if "/transactions" in u), 2)

    def test_empty_transactions(self):
        _, c = make()
        self.assertEqual(c.list_transactions("SIM-ACCT-000202"), [])

    def test_token_reused(self):
        m, c = make()
        c.get_account(ACCT)
        c.get_account("SIM-ACCT-000202")
        self.assertEqual(count(m, "/oauth/token"), 1)

    def test_not_found_and_forbidden(self):
        _, c = make()
        with self.assertRaises(vc.NotFoundError):
            c.get_account("SIM-ACCT-999999")
        _, c = make(client_id="SIMULATION-client-noscope")
        with self.assertRaises(vc.AuthorizationError):
            c.get_account(ACCT)


class AuthenticationFailure(unittest.TestCase):
    def test_invalid_client_scenario(self):
        m, c = make("auth_invalid_client")
        with self.assertRaises(vc.AuthenticationError):
            c.get_account(ACCT)
        self.assertEqual(len(m.calls), 1)  # no resource call after failed auth

    def test_wrong_secret(self):
        _, c = make(secret="SIMULATION-wrong")
        with self.assertRaises(vc.AuthenticationError):
            c.get_account(ACCT)

    def test_unknown_client(self):
        _, c = make(client_id="SIMULATION-nobody")
        with self.assertRaises(vc.AuthenticationError):
            c.get_account(ACCT)

    def test_token_rejected_reauths_once_then_fails(self):
        m, c = make("auth_token_rejected")
        with self.assertRaises(vc.AuthenticationError):
            c.get_account(ACCT)
        self.assertEqual(count(m, "/oauth/token"), 2)
        self.assertEqual(count(m, "/v1/accounts"), 2)

    def test_expired_token_recovers(self):
        m, c = make("auth_token_expired_once")
        self.assertEqual(c.get_account(ACCT)["account_id"], ACCT)
        self.assertEqual(count(m, "/oauth/token"), 2)

    def test_secret_never_leaks_into_errors_or_repr(self):
        _, c = make("auth_invalid_client")
        with self.assertRaises(vc.AuthenticationError) as cm:
            c.get_account(ACCT)
        self.assertNotIn(SECRET, str(cm.exception))
        self.assertNotIn(SECRET, repr(c))


class Timeout(unittest.TestCase):
    def test_persistent_timeout_raises_after_bounded_retries(self):
        m, c = make("timeout", max_retries=2)
        with self.assertRaises(vc.VendorTimeoutError):
            c.get_account(ACCT)
        self.assertEqual(count(m, "/v1/accounts"), 3)
        self.assertEqual(c.sleeps, [2, 4])  # exponential backoff, injected sleep (no real wait)

    def test_transient_timeout_recovers(self):
        _, c = make("timeout_once")
        self.assertEqual(c.get_account(ACCT)["status"], "OPEN")
        self.assertEqual(c.sleeps, [2])

    def test_latency_above_client_timeout(self):
        m, c = make(timeout=0.001, max_retries=0)
        m.latency_s = 0.5
        with self.assertRaises(vc.VendorTimeoutError) as cm:
            c.get_account(ACCT)
        self.assertIn("timed out", str(cm.exception))


class RateLimiting(unittest.TestCase):
    def test_429_once_honours_retry_after_then_succeeds(self):
        _, c = make("rate_limit_once")
        self.assertEqual(c.get_account(ACCT)["account_id"], ACCT)
        self.assertEqual(c.sleeps, [1])

    def test_429_always_exhausts_retries(self):
        m, c = make("rate_limit_always", max_retries=3)
        with self.assertRaises(vc.RateLimitedError) as cm:
            c.get_account(ACCT)
        self.assertEqual(cm.exception.retry_after, 1)
        self.assertEqual(c.sleeps, [1, 1, 1])
        self.assertEqual(count(m, "/v1/accounts"), 4)

    def test_retry_after_above_cap_fails_fast_without_sleeping(self):
        _, c = make("rate_limit_long", max_retry_after=30)
        with self.assertRaises(vc.RateLimitedError) as cm:
            c.get_account(ACCT)
        self.assertEqual(cm.exception.retry_after, 3600)
        self.assertEqual(c.sleeps, [])

    def test_non_numeric_retry_after_is_malformed(self):
        _, c = make("rate_limit_bad_retry_after")
        with self.assertRaises(vc.MalformedResponseError):
            c.get_account(ACCT)
        self.assertEqual(c.sleeps, [])

    def test_missing_retry_after_is_malformed(self):
        _, c = make("rate_limit_no_retry_after")
        with self.assertRaises(vc.MalformedResponseError):
            c.get_account(ACCT)


class MalformedResponses(unittest.TestCase):
    def test_every_malformed_scenario_fails_closed(self):
        scen = [s for s in SCENARIOS if s.startswith("malformed_")]
        self.assertGreaterEqual(len(scen), 9)
        calls = {"get_account": lambda c: c.get_account(ACCT),
                 "list_transactions": lambda c: c.list_transactions(ACCT)}
        for s in scen:
            for name, call in calls.items():
                with self.subTest(scenario=s, call=name):
                    _, c = make(s)
                    with self.assertRaises(vc.MalformedResponseError):
                        call(c)

    def test_extra_pii_field_is_rejected_not_passed_through(self):
        _, c = make("malformed_extra_field")
        with self.assertRaises(vc.MalformedResponseError) as cm:
            c.get_account(ACCT)
        self.assertIn("unexpected properties", str(cm.exception))


class Offline(unittest.TestCase):
    def test_sockets_are_blocked(self):
        with self.assertRaises(_offline.NetworkBlocked):
            socket.create_connection(("acme-core-ledger.simulation.invalid", 443))


if __name__ == "__main__":
    unittest.main()
