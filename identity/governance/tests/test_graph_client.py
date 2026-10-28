"""graph_client: paging, throttling, auth failures -- mocked transports only (no network).

Run:  python3 -m unittest discover -s identity/governance/tests -v
"""
import os
import unittest

import _common  # noqa: F401
import graph_client as gc

G = gc.GRAPH_ROOT


class ScriptedTransport(object):
    """In-memory transport: {path: [Response, ...]}; last response repeats."""

    def __init__(self, script):
        self.script = script
        self.calls = []
        self.n = {}

    def get(self, url):
        assert url.startswith(G), url
        key = url[len(G):]
        self.calls.append(key)
        seq = self.script[key]
        i = self.n.get(key, 0)
        self.n[key] = i + 1
        return seq[min(i, len(seq) - 1)]


def ok(items, nxt=None):
    b = {"value": items}
    if nxt:
        b["@odata.nextLink"] = G + nxt
    return gc.Response(200, b)


def error(status, code="X", headers=None):
    return gc.Response(status, {"error": {"code": code, "message": "synthetic",
                                          "innerError": {"request-id": "rid-%d" % status}}}, headers)


class Sleeps(list):
    def __call__(self, s):
        self.append(s)


class TestPaging(unittest.TestCase):
    def test_follows_next_link_across_three_pages(self):
        t = ScriptedTransport({"/x": [ok([1, 2], "/x?$skiptoken=2")], "/x?$skiptoken=2": [ok([3], "/x?$skiptoken=3")],
                               "/x?$skiptoken=3": [ok([4])]})
        c = gc.GraphClient(t)
        self.assertEqual(c.list_all("/x"), [1, 2, 3, 4])
        self.assertEqual(t.calls, ["/x", "/x?$skiptoken=2", "/x?$skiptoken=3"])
        self.assertEqual(c.pages_fetched, 3)

    def test_empty_collection(self):
        self.assertEqual(gc.GraphClient(ScriptedTransport({"/x": [ok([])]})).list_all("/x"), [])

    def test_next_link_loop_fails_closed(self):
        t = ScriptedTransport({"/x": [ok([1], "/x")]})
        with self.assertRaises(gc.GraphResponseError):
            gc.GraphClient(t).list_all("/x")

    def test_page_limit(self):
        script = {"/p0": [ok([0], "/p1")]}
        for i in range(1, 10):
            script["/p%d" % i] = [ok([i], "/p%d" % (i + 1))]
        with self.assertRaises(gc.GraphResponseError):
            gc.GraphClient(ScriptedTransport(script), max_pages=5).list_all("/p0")

    def test_missing_value_array_fails_closed(self):
        t = ScriptedTransport({"/x": [gc.Response(200, {"values": []})]})
        with self.assertRaises(gc.GraphResponseError):
            gc.GraphClient(t).list_all("/x")

    def test_non_string_next_link(self):
        t = ScriptedTransport({"/x": [gc.Response(200, {"value": [], "@odata.nextLink": 7})]})
        with self.assertRaises(gc.GraphResponseError):
            gc.GraphClient(t).list_all("/x")

    def test_non_object_body(self):
        t = ScriptedTransport({"/x": [gc.Response(200, "<html>")]})
        with self.assertRaises(gc.GraphResponseError):
            gc.GraphClient(t).list_all("/x")


class TestAuthorizationFailures(unittest.TestCase):
    def _assert_auth(self, status, code):
        t = ScriptedTransport({"/x": [error(status, code), ok([1])]})
        sl = Sleeps()
        with self.assertRaises(gc.GraphAuthError) as cm:
            gc.GraphClient(t, sleep=sl).list_all("/x")
        e = cm.exception
        self.assertEqual((e.status, e.code, e.request_id), (status, code, "rid-%d" % status))
        self.assertEqual(t.calls, ["/x"], "auth errors must never be retried")
        self.assertEqual(sl, [])
        self.assertEqual(e.as_dict()["kind"], "authorization")

    def test_401_not_retried(self):
        self._assert_auth(401, "InvalidAuthenticationToken")

    def test_403_not_retried(self):
        self._assert_auth(403, "Authorization_RequestDenied")

    def test_403_on_second_page_aborts_whole_collection(self):
        t = ScriptedTransport({"/x": [ok([1], "/x?p=2")], "/x?p=2": [error(403, "Authorization_RequestDenied")]})
        with self.assertRaises(gc.GraphAuthError):
            gc.GraphClient(t).list_all("/x")

    def test_other_4xx_is_response_error(self):
        t = ScriptedTransport({"/x": [error(404, "Request_ResourceNotFound")]})
        with self.assertRaises(gc.GraphResponseError) as cm:
            gc.GraphClient(t).list_all("/x")
        self.assertNotIsInstance(cm.exception, gc.GraphAuthError)


class TestThrottling(unittest.TestCase):
    def test_429_honours_retry_after_then_succeeds(self):
        t = ScriptedTransport({"/x": [error(429, "TooManyRequests", {"Retry-After": "7"}),
                                      error(429, "TooManyRequests", {"retry-after": "2"}), ok([1])]})
        sl = Sleeps()
        c = gc.GraphClient(t, sleep=sl)
        self.assertEqual(c.list_all("/x"), [1])
        self.assertEqual(sl, [7, 2])
        self.assertEqual([r["retryAfterHeader"] for r in c.retry_log], ["7", "2"])

    def test_429_without_retry_after_uses_exponential_backoff(self):
        t = ScriptedTransport({"/x": [error(429), error(429), error(429), ok([])]})
        sl = Sleeps()
        gc.GraphClient(t, sleep=sl).list_all("/x")
        self.assertEqual(sl, [1, 2, 4])

    def test_unparseable_retry_after_falls_back(self):
        t = ScriptedTransport({"/x": [error(429, headers={"Retry-After": "Wed, 28 Oct 2026 12:00:00 GMT"}), ok([])]})
        sl = Sleeps()
        gc.GraphClient(t, sleep=sl).list_all("/x")
        self.assertEqual(sl, [1])

    def test_retry_after_is_capped(self):
        t = ScriptedTransport({"/x": [error(429, headers={"Retry-After": "86400"}), ok([])]})
        sl = Sleeps()
        gc.GraphClient(t, sleep=sl, max_retry_after=60).list_all("/x")
        self.assertEqual(sl, [60])

    def test_503_and_504_are_retried(self):
        t = ScriptedTransport({"/x": [error(503), error(504), ok([5])]})
        self.assertEqual(gc.GraphClient(t, sleep=Sleeps()).list_all("/x"), [5])

    def test_retry_budget_exhausted(self):
        t = ScriptedTransport({"/x": [error(429, "TooManyRequests", {"Retry-After": "1"})]})
        sl = Sleeps()
        with self.assertRaises(gc.GraphThrottledError) as cm:
            gc.GraphClient(t, max_retries=3, sleep=sl).list_all("/x")
        self.assertEqual(len(t.calls), 4)
        self.assertEqual(sl, [1, 1, 1])
        self.assertEqual(cm.exception.status, 429)

    def test_throttle_mid_pagination_resumes_same_page(self):
        t = ScriptedTransport({"/x": [ok([1], "/x?p=2")],
                               "/x?p=2": [error(429, headers={"Retry-After": "1"}), ok([2])]})
        self.assertEqual(gc.GraphClient(t, sleep=Sleeps()).list_all("/x"), [1, 2])
        self.assertEqual(t.calls, ["/x", "/x?p=2", "/x?p=2"])


class TestFixtureTransport(unittest.TestCase):
    def test_refuses_non_graph_url(self):
        t = gc.FixtureTransport(os.path.join(_common.SCEN, "baseline"))
        with self.assertRaises(gc.GraphResponseError):
            t.get("https://login.microsoftonline.com/common/oauth2/v2.0/token")

    def test_unknown_route_is_graph_404(self):
        t = gc.FixtureTransport(os.path.join(_common.SCEN, "baseline"))
        r = t.get(G + "/me")
        self.assertEqual(r.status, 404)
        self.assertEqual(r.body["error"]["code"], "Request_ResourceNotFound")

    def test_inherit_overrides_parent_route(self):
        t = gc.FixtureTransport(os.path.join(_common.SCEN, "auth-401"))
        self.assertEqual(t.meta["asOfUtc"], "2026-10-28T12:00:00Z")
        r = t.get(G + "/roleManagement/directory/roleDefinitions?$select=id,displayName,templateId,isBuiltIn")
        self.assertEqual(r.status, 401)

    def test_sequence_last_response_repeats(self):
        t = gc.FixtureTransport(os.path.join(_common.SCEN, "throttled-recover"))
        url = G + "/roleManagement/directory/roleAssignmentScheduleInstances"
        self.assertEqual([t.get(url).status for _ in range(4)], [429, 429, 200, 200])


if __name__ == "__main__":
    unittest.main()
