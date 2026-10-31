"""Static, credential-free documentation build. Never executes document commands."""
import hashlib
import html
import json
import posixpath
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import bleach
import jsonschema
import markdown
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'dist/docs'
REPO = 'https://github.com/onnxscibroccoli/bank-it-operations-lab'
STATES = ['Concept','Proposed','Planned','In Development','Experimental','Simulated','Locally Verified','CI Verified','Integration Verified','Production Verified','Stable','Deprecated','Archived']
def render(text):
    return bleach.clean(markdown.markdown(text, extensions=['tables','fenced_code','toc']), tags={'p','h1','h2','h3','h4','h5','h6','a','ul','ol','li','strong','em','code','pre','blockquote','table','thead','tbody','tr','th','td','hr','br','details','summary'}, attributes={'a':['href','title'], '*':['id'], 'code':['class']}, protocols=['http','https','mailto'], strip=True)
def validate_metadata(data):
    jsonschema.validate(data, json.loads((ROOT/'docs/metadata/schema.json').read_text()))
    required = {str(p.relative_to(ROOT)) for p in (ROOT/'docs/knowledge').glob('*.md')}
    if required - set(data): raise ValueError(f'Missing metadata: {sorted(required-set(data))}')
    ids = set()
    for path, m in data.items():
        if not (ROOT/path).is_file(): raise ValueError(f'Missing document {path}')
        if m['id'] in ids: raise ValueError('Duplicate id')
        ids.add(m['id'])
        for source in m['source_files']:
            if not (ROOT/source).exists(): raise ValueError(f'Missing source {source}')
        if m['verification']['level'] != 'Not established' and not m['verification']['evidence']:
            raise ValueError(f'Verification requires evidence: {path}')
def files():
    tracked = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'], cwd=ROOT, text=True).splitlines()
    return sorted(set(p for p in tracked if p.lower().endswith('.md') and (ROOT/p).is_file()))
def page_url(path): return 'pages/'+path[:-3]+'.html'
def build():
    metadata = json.loads((ROOT/'docs/metadata/pages.json').read_text())
    validate_metadata(metadata)
    sha = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    paths = files(); pathset=set(paths); pages=[]; broken=[]
    OUT.mkdir(parents=True, exist_ok=True)
    # Remove obsolete rendered pages, while preserving separate validation reports.
    if (OUT/'pages').exists(): shutil.rmtree(OUT/'pages')
    for asset in ['style.css','search.js','search-core.js']:
        shutil.copyfile(ROOT/'scripts/docs'/asset, OUT/asset)
    def frame(title, content, prefix):
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="IT operations learning and source-backed lab reference"><title>{html.escape(title)} · IT Operations Knowledge Base</title><link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Skip to content</a><header><p class="brand">IT Operations Knowledge Base</p><nav aria-label="Primary"><a href="{prefix}index.html">Search and browse</a><a href="{prefix}pages/docs/knowledge/start.html">Start learning</a><a href="{prefix}pages/docs/knowledge/development.html">Current development</a><a href="{prefix}pages/docs/knowledge/ai.html">Learn with AI</a></nav></header><main id="main" tabindex="-1">{content}</main><footer>Living laboratory • Evidence has a scope • No production verification implied</footer></body></html>'''
    for path in paths:
        text=(ROOT/path).read_text(); title=re.search(r'^# (.+)',text,re.M)
        title=title.group(1) if title else Path(path).stem
        m=metadata.get(path)
        status=m['lifecycle_status'] if m else 'Unreviewed legacy documentation'
        category=m['category'] if m else path.split('/')[0]
        plain=html.unescape(re.sub('<[^>]+>', ' ', render(text)))
        plain=re.sub(r'\s+',' ',plain).strip()
        page={'id':m['id'] if m else 'legacy:'+path,'path':path,'title':title,'description':m['description'] if m else plain[:180], 'text':plain,'category':category,'status':status,'audience':m['audience'] if m else ['reference'],'aliases':m.get('aliases',[]) if m else [],'url':page_url(path),'sha256':hashlib.sha256(text.encode()).hexdigest(),'metadata':m}
        pages.append(page)
        prefix=posixpath.relpath('.',posixpath.dirname(page['url']))+'/'
        def link(match):
            href=html.unescape(match.group(1)); u=urlsplit(href)
            if u.scheme or u.netloc or href.startswith('#'): return match.group(0)
            target=posixpath.normpath(posixpath.join(posixpath.dirname(path),unquote(u.path)))
            if (ROOT/target).is_dir() and target+'/README.md' in pathset: target+='/README.md'
            if not (ROOT/target).exists(): broken.append({'page':path,'target':href})
            if target in pathset:
                dest=prefix+page_url(target)
            else: dest=REPO+'/blob/'+sha+'/'+quote(target,safe='/')
            if u.fragment: dest+='#'+u.fragment
            return 'href="'+html.escape(dest,quote=True)+'"'
        body=re.sub(r'href="([^"]*)"',link,render(text))
        if m:
            state='<dl>'+''.join(f'<dt>{label}</dt><dd>{html.escape(str(value))}</dd>' for label,value in [('Current state',m['current_state']),('Verified behavior',m['verification']['scope']),('Known limitations',m['limitations']),('Planned development',m['planned']),('Last verified',m['verification']['last_verified'] or 'Not established'),('Related development',', '.join(m['related_development']) or 'No specific issue recorded')])+'</dl>'
        else:
            state='<p>This existing document has not yet received structured review. Claims below belong to its original context; historical evidence is not current validation. Last verified: not established by this portal. Next: review source and evidence before modernization.</p>'
        content=f'<aside aria-label="Documentation status"><strong>{html.escape(status)}</strong>{state}</aside>'+body+f'<p><a href="{REPO}/blob/{sha}/{quote(path,safe="/")}">Source at build parent commit</a> · Local source: <code>{html.escape(path)}</code></p>'
        dest=OUT/page['url']; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(frame(title,content,prefix))
    catalog=''.join(f'<li><a href="{html.escape(p["url"])}">{html.escape(p["title"])}</a> — {html.escape(p["category"])} · {html.escape(p["status"])}</li>' for p in pages)
    home='''<h1>Understand IT. Practice with evidence.</h1><p>Start with a question, explore a topic, or inspect how a laboratory test works. You do not need to know the repository structure.</p><p>This is an evolving educational resource. Lab demonstrations, proposals, and historical records are clearly distinguished.</p><form id="search-form" role="search"><label for="query">Find a topic or ask an IT question</label><input id="query" name="q" type="search" placeholder="How do I recover a database?"><label for="category">Subject</label><select id="category"><option value="">All subjects</option></select><label for="status">Documentation status</label><select id="status"><option value="">All statuses</option></select><button type="submit">Search</button></form><p id="search-status" role="status" aria-live="polite">Loading search. You can browse all documents below.</p><ol id="results"></ol><noscript><p>Search needs JavaScript. All documentation remains available in the catalog below.</p></noscript><h2>Choose a starting point</h2><ul><li><a href="pages/docs/knowledge/start.html">Start learning and browse topics</a></li><li><a href="pages/docs/knowledge/identity.html">Practical tutorial: employee permissions</a></li><li><a href="pages/docs/knowledge/recovery.html">Database recovery and technical reference</a></li><li><a href="pages/docs/knowledge/incident.html">Troubleshoot an outage</a></li><li><a href="pages/docs/knowledge/glossary.html">Technical glossary</a></li></ul><h2>All documentation</h2><p>Legacy documents are indexed without changing their evidence or claiming a new review.</p><ul>'''+catalog+'</ul><script type="module" src="search.js"></script>'
    (OUT/'index.html').write_text(frame('Search and learn',home,''))
    (OUT/'search-index.json').write_text(json.dumps(pages,ensure_ascii=False))
    (OUT/'metadata.json').write_text(json.dumps({'schema_version':1,'repository':REPO,'build_parent_commit':sha,'pages':[{k:v for k,v in p.items() if k!='text'} for p in pages]},indent=2))
    report={'indexed':len(pages),'structured':len(metadata),'legacy':len(pages)-len(metadata),'broken_legacy_links':broken,'build_parent_commit':sha}
    (OUT/'coverage.json').write_text(json.dumps(report,indent=2))
    (OUT/'.nojekyll').write_text('')
    (OUT/'llms.txt').write_text('# IT Operations Knowledge Base\n\nRead metadata.json for page status and source relationships.\nRead search-index.json for plain text.\nRead pages/docs/knowledge/ai.html for safety and teaching guidance.\nNever infer verification from search ranking.\n')
    strict=[b for b in broken if b['page'] in metadata]
    if strict: raise ValueError(f'Broken curated links: {strict}')
    print(json.dumps({'indexed':len(pages),'structured':len(metadata),'legacy_link_findings':len(broken)}))
if __name__=='__main__': build()
