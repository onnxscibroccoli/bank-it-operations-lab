"""Real Ed25519 signatures; ephemeral test keys never enrolled in the repository."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_owner_attestation import canonical, fingerprint, verify

class SignatureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
  subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(cls.root/'test-key.pem')],check=True,capture_output=True)
  der=subprocess.check_output(['openssl','pkey','-in',str(cls.root/'test-key.pem'),'-pubout','-outform','DER'])
  cls.public=der[-32:];cls.fp=fingerprint(cls.public)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):
  self.payload={'schema':'bank-lab/owner-attestation/v1','repository':'onnxscibroccoli/bank-it-operations-lab','candidateSha':'a'*40,'mainSha':'b'*40,'testedMergeSha':'c'*40,'workflowRun':'12345678','criterion':'EXCEPTION','exceptionId':'EX-04','scope':'AwsSolutions-IAM5 DbBackupPolicy','decision':'APPROVED','keyFingerprint':self.fp}
  self.expected={k:self.payload[k] for k in ('repository','candidateSha','mainSha','testedMergeSha','workflowRun','criterion','exceptionId','scope')}
  self.keys={self.fp:self.public}
 def sign(self,payload=None):
  (self.root/'payload').write_bytes(canonical(self.payload if payload is None else payload))
  subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(self.root/'test-key.pem'),'-in',str(self.root/'payload'),'-out',str(self.root/'signature')],check=True,capture_output=True)
  return base64.b64encode((self.root/'signature').read_bytes()).decode()
 def test_valid_signature_and_binding(self):self.assertTrue(verify(self.payload,self.sign(),self.keys,self.expected))
 def test_changed_payload_rejected(self):
  sig=self.sign();self.payload['scope']='different';self.assertFalse(verify(self.payload,sig,self.keys,self.expected))
 def test_other_candidate_repository_run_and_scope_rejected(self):
  sig=self.sign()
  for key in ('candidateSha','mainSha','testedMergeSha','repository','workflowRun','scope'):
   expected=dict(self.expected);expected[key]='wrong';self.assertFalse(verify(self.payload,sig,self.keys,expected))
 def test_missing_binding_rejected(self):self.assertFalse(verify(self.payload,self.sign(),self.keys))
 def test_unknown_key_rejected(self):self.assertFalse(verify(self.payload,self.sign(),{} ,self.expected))
 def test_invalid_signature_rejected(self):self.assertFalse(verify(self.payload,base64.b64encode(b'x'*64).decode(),self.keys,self.expected))
 def test_junk_base64_rejected(self):self.assertFalse(verify(self.payload,self.sign()+'!',self.keys,self.expected))
 def test_signed_missing_fields_rejected(self):
  del self.payload['candidateSha'];self.assertFalse(verify(self.payload,self.sign(),self.keys,self.expected))
 def test_signed_unknown_fields_rejected(self):
  self.payload['unexpected']=True;self.assertFalse(verify(self.payload,self.sign(),self.keys,self.expected))
 def test_signed_invalid_sha_rejected(self):
  self.payload['candidateSha']='abc';self.expected['candidateSha']='abc';self.assertFalse(verify(self.payload,self.sign(),self.keys,self.expected))
 def test_signed_unknown_decision_rejected(self):
  self.payload['decision']='MAYBE';self.assertFalse(verify(self.payload,self.sign(),self.keys,self.expected))
 def test_rejection_authenticates_but_is_not_an_approval(self):
  self.payload['decision']='REJECTED';self.assertTrue(verify(self.payload,self.sign(),self.keys,self.expected))
if __name__=='__main__':unittest.main()
