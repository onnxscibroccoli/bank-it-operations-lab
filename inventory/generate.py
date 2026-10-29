#!/usr/bin/env python3
"""Derive static resource inventory and dependency diagrams from CloudFormation JSON.
No SDK, credentials, subprocesses or network calls. Templates are never executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def references(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'Ref' and isinstance(item, str):
                yield item
            elif key == 'Fn::GetAtt':
                if isinstance(item, list) and item and isinstance(item[0], str): yield item[0]
                elif isinstance(item, str): yield item.split('.')[0]
            elif key == 'DependsOn':
                for name in [item] if isinstance(item, str) else item:
                    if isinstance(name, str): yield name
            yield from references(item)
    elif isinstance(value, list):
        for item in value: yield from references(item)

def build(paths):
    if not paths: raise ValueError('At least one template is required')
    sources, assets, edges = [], [], set()
    seen = set()
    for path in sorted(paths):
        raw = path.read_bytes(); template = json.loads(raw)
        resources = template.get('Resources')
        if not isinstance(resources, dict) or not resources: raise ValueError(f'{path.name}: nonempty Resources required')
        stack = path.name.removesuffix('.template.json')
        if stack in seen: raise ValueError('Duplicate stack name')
        seen.add(stack)
        sources.append({'template':path.name,'sha256':hashlib.sha256(raw).hexdigest()})
        for name, resource in sorted(resources.items()):
            if not isinstance(resource,dict) or not re.fullmatch(r'(?:[A-Za-z0-9]+::[A-Za-z0-9]+::[A-Za-z0-9]+|Custom::[A-Za-z0-9_]+)',resource.get('Type','')):
                raise ValueError(f'{name}: invalid resource Type')
            assets.append({'id':f'{stack}:{name}','stack':stack,'logical_id':name,'type':resource['Type'],'status':'STATIC_REFERENCE'})
            for target in references(resource):
                if target in resources and target != name: edges.add((f'{stack}:{name}',f'{stack}:{target}'))
    return {'schema':'bank-lab/static-inventory/v1','execution_status':'NOT_DEPLOYED','sources':sources,'resources':assets,'edges':[{'from':a,'to':b} for a,b in sorted(edges)]}

def render(data):
    lines=['# Generated architecture inventory','','STATIC_REFERENCE — NOT_DEPLOYED. Arrows show template references/dependencies, not observed network traffic. Implicit service behavior and references embedded in Fn::Sub strings are not inferred.','','| Stack | Type | Count |','|---|---|---|']
    counts={}
    for r in data['resources']: counts[(r['stack'],r['type'])]=counts.get((r['stack'],r['type']),0)+1
    for (stack,kind),n in sorted(counts.items()): lines.append(f'| {stack} | {kind} | {n} |')
    # Scope each diagram to one resource and at most four explicit dependencies.
    assets={r['id']:r for r in data['resources']}
    for source in sorted({e['from'] for e in data['edges']}):
        targets=[e['to'] for e in data['edges'] if e['from']==source]
        for start in range(0,len(targets),4):
            lines += ['',f"### {assets[source]['logical_id']} ({assets[source]['stack']})",'','```mermaid','flowchart TD',f'  source["{assets[source]["logical_id"]}"]']
            for i,target in enumerate(targets[start:start+4]):
                lines += [f'  n{i}["{assets[target]["logical_id"]}"]',f'  source --> n{i}']
            lines.append('```')
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--templates',type=Path,default=ROOT/'evidence/aws/aws-remediation-vpc-rds/synth'); args=ap.parse_args()
    data=build(list(args.templates.glob('*.template.json')))
    outputs={ROOT/'inventory/assets.json':json.dumps(data,indent=2)+'\n', ROOT/'inventory/ARCHITECTURE.md':render(data)}
    for path,text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text()!=text: raise SystemExit(f'DRIFT: {path.name}')
        else:path.write_text(text)
    print(f'STATIC inventory: {len(data["resources"])} resources; {len(data["edges"])} dependencies; NOT_DEPLOYED')
if __name__=='__main__': main()
