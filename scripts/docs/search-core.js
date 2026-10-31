// Transparent token scoring. No remote calls, model, tracking, or query logs.
const stop = new Set('a an the is are do does how what when why i to from of for with can company it departments'.split(' '));
const groups = [
 ['backup','backups','recover','recovery','restore','restoration','crashes','crash','database','postgresql'],
 ['permissions','permission','access','employee','employees','privilege','rbac','identity','authorization'],
 ['authentication','authorization','login','identity'],
 ['outages','outage','stopped','incident','investigate','detect','monitoring','observability','cyberattack'],
 ['infrastructure','iac','code','cdk','terraform'],
 ['automate','automation','routine','maintenance','patching']
];
export function tokens(s){return (s.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(t=>!stop.has(t));}
export function search(pages,query,category='',status=''){
 const original=tokens(query), expanded=new Set(original);
 for(const group of groups) if(group.some(t=>original.includes(t))) group.forEach(t=>expanded.add(t));
 return pages.filter(p=>(!category||p.category===category)&&(!status||p.status===status)).map(p=>{
 const heading=new Set(tokens(p.title+' '+p.description+' '+p.aliases.join(' '))),body=new Set(tokens(p.text));
 let score=0; for(const t of expanded) score+=(heading.has(t)?(original.includes(t)?8:2):0)+(body.has(t)?(original.includes(t)?2:0.4):0);
 if(score && p.metadata)score+=3;
 return {...p,score};
 }).filter(p=>!original.length||p.score>0).sort((a,b)=>b.score-a.score||a.path.localeCompare(b.path));
}
