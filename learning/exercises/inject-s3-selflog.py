#!/usr/bin/env python3
"""Week 2/3 failure injection: re-add self-logging to AccessLogsBucket in a COPY of a synthesized template.

usage: inject-s3-selflog.py <template.json> > /tmp/injected.json
Then run: python3 $PR3/evidence/shared/validate_evidence.py cfn-s3-selflog /tmp/injected.json   (expect exit 1)
"""
import json, sys
t = json.load(open(sys.argv[1]))
for k, v in t["Resources"].items():
    if v["Type"] == "AWS::S3::Bucket" and k.startswith("AccessLogsBucket"):
        v.setdefault("Properties", {})["LoggingConfiguration"] = {"LogFilePrefix": "self-access-logs/"}
json.dump(t, sys.stdout)
