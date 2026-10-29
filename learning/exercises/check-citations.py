"""Citation check for learning/** and docs/adr/**.
Usage: LAB_REPO=/path/to/clone-with-all-branches python3 learning/exercises/check-citations.py
Checks: every `branch@sha:path` has sha == current origin/branch head and path exists at sha;
every bare backticked path exists on some branch (exact, or as a module-relative suffix)."""
import re, subprocess, sys, glob, fnmatch, os
REPO=os.environ.get('LAB_REPO','.')
GUIDE=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUFFIX=False
def git(*a): return subprocess.run(['git','-C',REPO,*a],capture_output=True,text=True)
branches=[b.strip().replace('origin/','') for b in git('branch','-r','--format=%(refname:short)').stdout.split() if b.startswith('origin/') and b!='origin/HEAD']
heads={b:git('rev-parse','origin/'+b).stdout.strip() for b in branches}
files={}
def tree(ref):
    if ref not in files: files[ref]=git('ls-tree','-r','--name-only',ref).stdout.split('\n')
    return files[ref]
def expand(p):
    m=re.search(r'\{([^}]*)\}',p)
    if not m: return [p]
    return sum([expand(p[:m.start()]+x+p[m.end():]) for x in m.group(1).split(',')],[])
def exists(ref,p):
    t=tree(ref); p=p.rstrip('/').split('#')[0].split(':')[0] if not re.search(r':\d+$',p) else p.rsplit(':',1)[0]
    pats=[p] + ([p+'/**'] if '*' not in p else [])
    p=p.split(' ')[0]
    for q in expand(p):
        if q in t: return True
        if SUFFIX and any(f.endswith('/'+q) for f in t): return True
        if SUFFIX and '*' in q and any(fnmatch.fnmatch(f,'*/'+q.replace('**','*')) for f in t): return True
        if any(f.startswith(q.rstrip('/')+'/') for f in t): return True
        if '*' in q and any(fnmatch.fnmatch(f,q.replace('**','*')) for f in t): return True
    return False
roots=glob.glob(GUIDE+'/learning/**/*.md',recursive=True)+glob.glob(GUIDE+'/docs/adr/*.md')
bad=[]; n_pin=0; n_bare=0; stale=[]
pin=re.compile(r'`([A-Za-z0-9/_.-]+)@([0-9a-f]{7,40}):([^`]+)`')
for f in roots:
    s=open(f).read()
    for m in pin.finditer(s):
        b,sha,path=m.groups(); n_pin+=1
        if b not in heads: bad.append((f,m.group(0),'unknown branch')); continue
        if not heads[b].startswith(sha): stale.append((f,m.group(0),'head is '+heads[b][:7]))
        if not exists(sha,path): bad.append((f,m.group(0),'path missing at sha'))
    for m in re.finditer(r'`([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.*{},-]+)+(?:\.[a-z]{1,5})?(?::\d+)?)`',s):
        p=m.group(1)
        if '@' in p or p.startswith(('$','/','http','../','./')) or p.startswith('learning/') or p.startswith('docs/adr/0') or p.startswith('/tmp'): continue
        if p in ('kms:Create*','kms:Put*'): continue
        n_bare+=1
        if p in branches: continue
        if any(os.path.exists(GUIDE+'/learning/'+x) for x in expand(p)): continue
        SUFFIX=False
        if any(exists('origin/'+b,p) for b in branches): continue
        SUFFIX=True
        ok=any(exists('origin/'+b,p) for b in branches); SUFFIX=False
        if ok: print('SUFFIX-OK',os.path.relpath(f,GUIDE),p); continue
        if True:
            bad.append((f,p,'bare path not on any branch'))
# local learning/docs links
for f in roots:
    for m in re.finditer(r'`(learning/[^`]+|docs/adr/[^`]+)`',open(f).read()):
        p=m.group(1).split(' ')[0]; n_bare+=1
        if not glob.glob(GUIDE+'/'+p.split('#')[0]) and not any(glob.glob(GUIDE+'/'+q) for q in expand(p)) and not p.endswith(('/','**')):
            bad.append((f,p,'local path missing'))
for x in stale: print('STALE',*x)
for x in bad: print('BAD',*x)
print(f'pinned={n_pin} bare={n_bare} stale={len(stale)} bad={len(bad)}')
