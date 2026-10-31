#!/usr/bin/env python3
"""Validate synthetic endpoint policy data, never apply it or call a tenant."""
import csv
import ipaddress
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent

def validate(baseline,policy,rules):
 errors=[]
 if not isinstance(baseline,dict) or baseline.get('schema')!='bank-lab/intune-compliance-baseline/v1':return ['invalid baseline schema']
 if baseline.get('executed') is not False:errors.append('baseline must be unexecuted')
 settings=baseline.get('settings',{})
 if not isinstance(settings,dict):return errors+['settings must be an object']
 for key in ('bitLocker','secureBoot','codeIntegrity','defenderRealTime','firewallDomain','firewallPrivate','firewallPublic'):
  if settings.get(key) is not True:errors.append(f'{key} must be true')
 length=settings.get('passwordMinimumLength')
 if type(length) is not int or not 14<=length<=128:errors.append('invalid minimum password length')
 if not isinstance(settings.get('osMinimumBuild'),str) or not re.fullmatch(r'\d+\.\d+\.\d+',settings['osMinimumBuild']):errors.append('invalid OS build')
 if not isinstance(policy,dict) or policy.get('defaultInboundAction')!='block' or policy.get('mode')!='PLAN_ONLY' or policy.get('executed') is not False:errors.append('invalid firewall profile: require PLAN_ONLY, default inbound block')
 if not isinstance(rules,list) or not rules:return errors+['rules must be a nonempty list']
 names=set()
 for rule in rules:
  if not isinstance(rule,dict):errors.append('invalid rule');continue
  name=rule.get('name');action=rule.get('action');port=rule.get('local_port');remote=rule.get('remote_address');proto=rule.get('protocol')
  if not isinstance(name,str) or not name or name in names:errors.append('missing/duplicate rule name')
  if isinstance(name,str):names.add(name)
  if rule.get('direction') not in ('inbound','outbound') or action not in ('allow','block') or proto not in ('tcp','udp','any'):errors.append('invalid direction/action/protocol')
  if port!='any' and (not isinstance(port,str) or not port.isdigit() or not 1<=int(port)<=65535):errors.append('invalid port')
  network=None
  if remote!='any':
   try:network=ipaddress.ip_network(remote,strict=True)
   except (ValueError,TypeError):errors.append('invalid CIDR')
  if action=='allow':
   if remote=='any' or network is None or network.prefixlen==0:errors.append('global allow forbidden')
   if port in ('any','22','3389','445','5985') or proto=='any':errors.append('broad/admin allow forbidden')
  if action=='block' and rule.get('direction')=='inbound' and port=='any' and remote=='any' and proto=='any':errors.append('explicit block-all overrides allow rules; use profile default instead')
 return errors

def main():
 baseline=json.loads((ROOT/'baselines/intune-compliance.json').read_text())
 policy=json.loads((ROOT/'baselines/firewall-policy.json').read_text())
 with (ROOT/'baselines/firewall-rules.csv').open(newline='') as f:rules=list(csv.DictReader(f))
 errors=validate(baseline,policy,rules)
 for error in errors:print('ERROR:',error)
 print('Endpoint baseline:', 'FAIL' if errors else 'PASS (static; NOT_EXECUTED)')
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())
