import {search,tokens} from './search-core.js';
const form=document.querySelector('#search-form'),query=document.querySelector('#query'),category=document.querySelector('#category'),status=document.querySelector('#status'),results=document.querySelector('#results'),announcement=document.querySelector('#search-status');
const el=(tag,text)=>{const n=document.createElement(tag);n.textContent=text;return n;};
try{
 const response=await fetch('search-index.json');if(!response.ok)throw new Error('index unavailable');
 const pages=await response.json();
 for(const [field,select] of [['category',category],['status',status]])for(const value of [...new Set(pages.map(p=>p[field]))].sort()){const o=el('option',value);o.value=value;select.append(o);}
 function update(){
  const found=search(pages,query.value,category.value,status.value);results.replaceChildren();
  for(const p of found.slice(0,30)){
   const li=el('li',''),a=el('a',p.title);a.href=p.url;li.append(a,el('p',p.description),el('p',p.category+' · '+p.status));
   const term=tokens(query.value).find(t=>p.text.toLowerCase().includes(t));const start=term?Math.max(0,p.text.toLowerCase().indexOf(term)-60):0;
   li.append(el('p',(start?'…':'')+p.text.slice(start,start+240)+'…'));results.append(li);
  }
  announcement.textContent=found.length?`${found.length} results. Showing ${Math.min(30,found.length)}.`:'No matching documents found. Try a shorter question or browse the catalog; this does not establish that a topic is absent.';
 }
 form.addEventListener('submit',e=>{e.preventDefault();update();});category.addEventListener('change',update);status.addEventListener('change',update);
 query.value=new URLSearchParams(location.search).get('q')||'';update();
}catch{announcement.textContent='Search could not load. Retry this page or use the complete document catalog below.';}
