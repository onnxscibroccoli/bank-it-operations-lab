"""Advisory source-to-documentation change report; does not demand irrelevant edits."""
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
base=os.environ.get('DOCS_BASE') or 'HEAD~1'
changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=ROOT,text=True).splitlines()
meta=json.loads((ROOT/'docs/metadata/pages.json').read_text())
affected=[]
for page,m in meta.items():
 sources=[p for p in changed if any(p==s or p.startswith(s+'/') for s in m['source_files'])]
 if sources: affected.append({'page':page,'changed_sources':sources,'page_changed':page in changed,'action':'Review factual claims and evidence; update only if behavior or explanation changed.'})
report={'base':base,'changed':changed,'affected':affected,'unmapped_sources':[p for p in changed if not p.endswith('.md') and not any(p in a['changed_sources'] for a in affected)],'limitations':'Advisory path mapping. Semantic drift and unregistered dependencies require review.'}
(ROOT/'dist/docs/impact.json').write_text(json.dumps(report,indent=2));print(f'{len(affected)} documentation pages may be affected; report is advisory')
