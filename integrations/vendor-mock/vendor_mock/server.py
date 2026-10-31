"""SIMULATION - optional loopback-only HTTP wrapper around the in-process mock, for manual
poking (e.g. `curl -s http://127.0.0.1:8099/v1/health`). NOT used by the tests, which never
open sockets. Binds 127.0.0.1 only.

    python3 -m vendor_mock.server --scenario normal --port 8099
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .mock import SCENARIOS, AcmeLedgerMock, SimulatedTimeout


def make_handler(mock: AcmeLedgerMock):
    class Handler(BaseHTTPRequestHandler):
        server_version = "AcmeCoreLedger-SIMULATION/0.1"

        def _do(self, method):
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(n) if n else b""
            try:
                r = mock.handle(method, self.path, dict(self.headers), body, timeout=30.0)
            except SimulatedTimeout:
                self.close_connection = True
                return  # drop the request without answering, like a hung upstream
            self.send_response(r.status)
            for k, v in r.headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(r.body)))
            self.end_headers()
            self.wfile.write(r.body)

        def do_GET(self):
            self._do("GET")

        def do_POST(self):
            self._do("POST")

    return Handler


def main():
    ap = argparse.ArgumentParser(description="SIMULATION Acme Core Ledger mock (loopback only)")
    ap.add_argument("--scenario", default="normal", choices=SCENARIOS)
    ap.add_argument("--port", type=int, default=8099)
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(AcmeLedgerMock(a.scenario)))
    print(f"SIMULATION mock on http://127.0.0.1:{a.port} scenario={a.scenario}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
