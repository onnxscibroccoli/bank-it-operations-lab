"""Read-only discovery report; registry claims are not converted to verification."""
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
modules=json.loads((ROOT/'coordination/modules.json').read_text())['modules']
pages=json.loads((ROOT/'dist/docs/search-index.json').read_text())
report={'scope':'Tracked and unignored working-tree files. Registry declarations are unverified claims, not fresh test results.','files':sorted(set(files)),'capabilities':[]}
for m in modules:
 docs=[p['path'] for p in pages if any(p['path']==x or p['path'].startswith(x+'/') for x in m['paths'])]
 report['capabilities'].append({'id':m['id'],'registry_state':m['status'],'source_paths':m['paths'],'documentation':docs,'declared_checks':m.get('required_checks',{}),'declared_evidence_classes':m.get('evidence_class',[]),'limitations':m.get('limitations',m.get('reason','Not documented in registry; review required.')),'related_prs':m.get('prs',[]),'fresh_verification':'Not established by inventory','coverage_gap':not bool(docs)})
(ROOT/'dist/docs/inventory.json').write_text(json.dumps(report,indent=2))
print(f"Inventoried {len(set(files))} files and {len(modules)} registered modules")
