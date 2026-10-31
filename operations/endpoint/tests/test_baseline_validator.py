import copy
import csv
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class BaselineValidation(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('endpoint_validator',ROOT/'validate_baseline.py')
  self.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.mod)
  self.baseline=json.loads((ROOT/'baselines/intune-compliance.json').read_text())
  self.policy={'defaultInboundAction':'block','mode':'PLAN_ONLY','executed':False}
  self.rules=[{'name':'https','direction':'inbound','action':'allow','protocol':'tcp','local_port':'443','remote_address':'10.42.0.0/16','comment':'synthetic'}]
 def test_valid_plan(self):self.assertEqual(self.mod.validate(self.baseline,self.policy,self.rules),[])
 def test_missing_required_setting_fails(self):
  del self.baseline['settings']['codeIntegrity'];self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_string_false_is_not_false(self):
  self.baseline['executed']='false';self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_bool_is_not_password_length(self):
  self.baseline['settings']['passwordMinimumLength']=True;self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_default_inbound_allow_rejected(self):
  self.policy['defaultInboundAction']='allow';self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_explicit_block_all_would_override_allow(self):
  self.rules.append({'name':'all','direction':'inbound','action':'block','protocol':'any','local_port':'any','remote_address':'any'})
  self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_global_ipv4_and_ipv6_allow_rejected(self):
  for cidr in ('0.0.0.0/0','::/0','any'):
   self.rules[0]['remote_address']=cidr;self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_admin_port_allow_rejected(self):
  for port in ('22','3389','445','5985'):
   self.rules[0]['local_port']=port;self.assertTrue(self.mod.validate(self.baseline,self.policy,self.rules))
 def test_invalid_rule_rejected(self):
  for field,value in [('protocol','bogus'),('local_port','65536'),('local_port','0'),('remote_address','not-a-network'),('direction','sideways')]:
   rule=copy.deepcopy(self.rules);rule[0][field]=value
   self.assertTrue(self.mod.validate(self.baseline,self.policy,rule))
 def test_empty_rules_rejected(self):self.assertTrue(self.mod.validate(self.baseline,self.policy,[]))
if __name__=='__main__':unittest.main()
