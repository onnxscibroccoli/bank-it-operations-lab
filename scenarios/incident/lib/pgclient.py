#!/usr/bin/env python3
"""SIMULATION - minimal stdlib PostgreSQL client (ctypes over libpq).

Used because the lab box may have the server binaries but no `psql`/`pg_isready`.
No third-party packages. Connection string comes from the CLI (no secrets: local trust auth).

  pgclient.py ping  "<conninfo>"              -> prints PQPING_* ; exit 0 only if PQPING_OK
  pgclient.py query "<conninfo>" -c "SQL"      -> rows as a|b|c ; exit 1 on any error
  pgclient.py query "<conninfo>" -f file.sql   -> statements split on ';' at end of line

libpq is located via $PG_LIBPQ, then $PG_BIN/../lib/libpq.so.5, then ctypes.util.find_library("pq").
"""
import ctypes
import ctypes.util
import os
import re
import sys

PING = {0: "PQPING_OK", 1: "PQPING_REJECT", 2: "PQPING_NO_RESPONSE", 3: "PQPING_NO_ATTEMPT"}
PGRES_COMMAND_OK, PGRES_TUPLES_OK, CONNECTION_OK = 1, 2, 0


def load_libpq():
    cands = [os.environ.get("PG_LIBPQ")]
    if os.environ.get("PG_BIN"):
        cands.append(os.path.join(os.environ["PG_BIN"], "..", "lib", "libpq.so.5"))
    cands.append(ctypes.util.find_library("pq"))
    for c in cands:
        if c and (os.path.exists(c) or not os.path.isabs(c)):
            try:
                lib = ctypes.CDLL(c)
                break
            except OSError:
                continue
    else:
        sys.stderr.write("SIMULATION pgclient: libpq not found (set PG_LIBPQ or PG_BIN)\n")
        sys.exit(127)
    lib.PQconnectdb.restype = ctypes.c_void_p
    lib.PQconnectdb.argtypes = [ctypes.c_char_p]
    lib.PQstatus.argtypes = [ctypes.c_void_p]
    lib.PQerrorMessage.restype = ctypes.c_char_p
    lib.PQerrorMessage.argtypes = [ctypes.c_void_p]
    lib.PQfinish.argtypes = [ctypes.c_void_p]
    lib.PQexec.restype = ctypes.c_void_p
    lib.PQexec.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.PQresultStatus.argtypes = [ctypes.c_void_p]
    lib.PQresultErrorMessage.restype = ctypes.c_char_p
    lib.PQresultErrorMessage.argtypes = [ctypes.c_void_p]
    lib.PQntuples.argtypes = [ctypes.c_void_p]
    lib.PQnfields.argtypes = [ctypes.c_void_p]
    lib.PQgetvalue.restype = ctypes.c_char_p
    lib.PQgetvalue.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.PQclear.argtypes = [ctypes.c_void_p]
    lib.PQping.argtypes = [ctypes.c_char_p]
    return lib


def split_sql(text):
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    return [s.strip() for s in re.split(r";\s*(?:\n|$)", text) if s.strip()]


def main(argv):
    if len(argv) < 3 or argv[1] not in ("ping", "query"):
        sys.stderr.write(__doc__)
        return 2
    lib = load_libpq()
    conninfo = argv[2].encode()
    if argv[1] == "ping":
        r = lib.PQping(conninfo)
        print(PING.get(r, "PQPING_UNKNOWN_%d" % r))
        return 0 if r == 0 else 1
    if len(argv) != 5 or argv[3] not in ("-c", "-f"):
        sys.stderr.write(__doc__)
        return 2
    sql = argv[4] if argv[3] == "-c" else open(argv[4], encoding="utf-8").read()
    conn = lib.PQconnectdb(conninfo)
    try:
        if lib.PQstatus(conn) != CONNECTION_OK:
            sys.stderr.write("connection failed: %s" % lib.PQerrorMessage(conn).decode(errors="replace"))
            return 1
        for stmt in split_sql(sql):
            res = lib.PQexec(conn, stmt.encode())
            st = lib.PQresultStatus(res)
            if st not in (PGRES_COMMAND_OK, PGRES_TUPLES_OK):
                sys.stderr.write(lib.PQresultErrorMessage(res).decode(errors="replace"))
                lib.PQclear(res)
                return 1
            if st == PGRES_TUPLES_OK:
                for i in range(lib.PQntuples(res)):
                    print("|".join((lib.PQgetvalue(res, i, j) or b"").decode()
                                   for j in range(lib.PQnfields(res))))
            lib.PQclear(res)
        return 0
    finally:
        lib.PQfinish(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
