"""Advisory availability checks, never a compliance or factual verification claim."""
import concurrent.futures,json,re,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
urls=sorted(set(u for p in (ROOT/'docs/knowledge').glob('*.md') for u in re.findall(r'https://[^\s)<>]+',p.read_text())))
def check(url):
 for attempt in range(2):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'BankITDocsLinkCheck/1.0'})
   with urllib.request.urlopen(req,timeout=8) as r: return {'url':url,'status':r.status,'destination':r.url,'meaning':'HTTP availability only'}
  except Exception as e: error=type(e).__name__
 return {'url':url,'status':'UNCONFIRMED','error':error,'meaning':'Network or remote restriction; manually review, do not infer invalid URL'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(check,urls))
(ROOT/'dist/docs/external-links.json').write_text(json.dumps({'checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results},indent=2));print(json.dumps(results))
