#!/usr/bin/env python3
"""Standalone Ed25519 verification prototype: stdlib plus OpenSSL 3.x.

NOT an active acceptance gate. Expected binding and enrolled keys must be supplied
by a trusted caller, outside the candidate. A valid signature also authenticates a
REJECTED decision; it is not itself approval. No keys are enrolled by this tool.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

BINDING=('repository','candidateSha','mainSha','testedMergeSha','workflowRun','criterion','exceptionId','scope')
FIELDS=set(BINDING)|{'schema','decision','keyFingerprint'}
HEX40=re.compile(r'^[0-9a-f]{40}$')

def canonical(payload):
    return json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def fingerprint(public_key_raw):
    return hashlib.sha256(public_key_raw).hexdigest()

def unique(pairs):
    out={}
    for key,value in pairs:
        if key in out: raise ValueError(f'duplicate JSON key: {key}')
        out[key]=value
    return out

def read_json(path):
    return json.loads(Path(path).read_text(),object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON number')))

def load_enrolled(path):
    document=read_json(path)
    if not isinstance(document,dict) or document.get('schema')!='bank-lab/enrolled-owner-keys/v1':raise ValueError('wrong enrolled key schema')
    if not isinstance(document.get('keys'),list):raise ValueError('keys must be a list')
    out={}
    for entry in document['keys']:
        raw=base64.b64decode(entry['publicKey'],validate=True)
        if len(raw)!=32 or entry['fingerprint']!=fingerprint(raw):raise ValueError('invalid enrolled Ed25519 public key/fingerprint')
        if entry['fingerprint'] in out:raise ValueError('duplicate enrolled key')
        out[entry['fingerprint']]=raw
    return out

def valid_payload(payload,expected):
    if not isinstance(payload,dict) or set(payload)!=FIELDS:return False
    if not isinstance(expected,dict) or set(expected)!=set(BINDING):return False
    if any(not isinstance(value,str) for value in payload.values()):return False
    if payload['schema']!='bank-lab/owner-attestation/v1':return False
    if any(payload[key]!=expected[key] for key in BINDING):return False
    if not all(HEX40.fullmatch(payload[key]) for key in ('candidateSha','mainSha','testedMergeSha')):return False
    if payload['candidateSha']==payload['testedMergeSha']:return False
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',payload['repository']):return False
    if not re.fullmatch(r'[1-9][0-9]{0,19}',payload['workflowRun']):return False
    if not re.fullmatch(r'[0-9a-f]{64}',payload['keyFingerprint']):return False
    if payload['criterion'] not in ('EXCEPTION','AC4','AC5') or payload['decision'] not in ('APPROVED','REJECTED'):return False
    if payload['criterion']=='EXCEPTION':
        if not re.fullmatch(r'[A-Z][A-Z0-9-]{1,30}',payload['exceptionId']) or not payload['scope'].strip():return False
    elif payload['exceptionId'] or payload['scope']:return False
    return True

def verify(payload,signature_b64,enrolled,expected=None):
    if not enrolled or not valid_payload(payload,expected):return False
    try:
        signature=base64.b64decode(signature_b64,validate=True)
        public=enrolled.get(payload['keyFingerprint'])
        if not isinstance(public,bytes) or len(public)!=32 or fingerprint(public)!=payload['keyFingerprint'] or len(signature)!=64:return False
        # RFC 8410 SubjectPublicKeyInfo prefix for a 32-byte Ed25519 public key.
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'public.der').write_bytes(bytes.fromhex('302a300506032b6570032100')+public)
            (root/'payload').write_bytes(canonical(payload));(root/'signature').write_bytes(signature)
            result=subprocess.run(['openssl','pkeyutl','-verify','-pubin','-keyform','DER','-inkey',str(root/'public.der'),'-rawin','-in',str(root/'payload'),'-sigfile',str(root/'signature')],capture_output=True,timeout=10)
            return result.returncode==0
    except (ValueError,TypeError,KeyError,OSError,subprocess.TimeoutExpired):return False

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload',required=True)
    parser.add_argument('--signature',required=True,help='base64 detached Ed25519 signature')
    parser.add_argument('--keys',required=True,help='independently enrolled public keys from trusted storage')
    parser.add_argument('--expected',required=True,help='expected exact binding produced by trusted runtime, not the payload')
    args=parser.parse_args(argv)
    try:
        payload=read_json(args.payload);keys=load_enrolled(args.keys)
        ok=verify(payload,args.signature,keys,read_json(args.expected))
    except (ValueError,TypeError,KeyError,OSError) as error:
        print(json.dumps({'signatureValid':False,'error':str(error),'mode':'VERIFIER_ONLY'}));return 2
    print(json.dumps({'signatureValid':ok,'decision':payload.get('decision') if ok else None,'approvalEffective':False,'mode':'VERIFIER_ONLY'}))
    return 0 if ok else 2
if __name__=='__main__':raise SystemExit(main())
