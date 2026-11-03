import {fileURLToPath} from 'node:url';
import path from 'node:path';
const repositoryRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
process.chdir(repositoryRoot);
import {chromium} from '@playwright/test';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true});
const page=await browser.newPage();
const root=process.env.DOCS_URL||'http://127.0.0.1:8000';
const report={environment:'Playwright Chromium, automated WCAG 2.2 AA subset',pages:[],keyboard:[],queries:[],manualScreenReader:'NOT RUN'};
try{
 await page.goto(root);await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('results.'));
 await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').textContent(),'Skip to content');
 await page.keyboard.press('Enter');assert.equal(await page.locator(':focus').getAttribute('id'),'main');report.keyboard.push('Skip link focuses main');
 const cases=[['How do backups work?','recovery'],['What happens when a database crashes?','recovery'],['What does least privilege mean?','identity'],['How do I control employee permissions?','identity'],['How can a company recover from a cyberattack?','recovery'],['What is infrastructure as code?','infrastructure'],['How do IT departments detect outages?','incident'],['How do I investigate why a service stopped working?','incident'],['What is the difference between authentication and authorization?','identity'],['How do I automate routine IT maintenance?','infrastructure']];
 for(const [query,id] of cases){await page.locator('#query').fill(query);await page.locator('#query').press('Enter');assert.ok((await page.locator('#results a').evaluateAll(a=>a.slice(0,5).map(x=>x.getAttribute('href')))).includes(`pages/docs/knowledge/${id}.html`));report.queries.push({query,expected:id,result:'PASS'});}
 await page.locator('#query').fill('zzzxnonexistentzz');await page.locator('#query').press('Enter');assert.match(await page.locator('#search-status').textContent(),/No matching/);
 await page.locator('#query').fill('permissions');await page.locator('#query').press('Enter');
 await page.locator('#query').press('Tab');assert.equal(await page.locator(':focus').getAttribute('id'),'category');
 await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').getAttribute('id'),'status');
 await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').getAttribute('id'),'level');
 await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').textContent(),'Search');
 await page.keyboard.press('Tab');assert.match(await page.locator(':focus').getAttribute('href'),/pages\//);report.keyboard.push('Search submit, subject/status/level filters and result link reachable by keyboard');
 await page.locator('#level').selectOption('beginner');await page.locator('#query').fill('recovery');await page.locator('#query').press('Enter');assert.match(await page.locator('#search-status').textContent(),/results/);report.levelFilter='Depth level filter returns results for beginner + recovery';await page.locator('#level').selectOption('');
 const sections=['start','topics','tutorials','reference','troubleshooting','development','ai'];
 for(const name of sections){
  await page.goto(`${root}/pages/docs/knowledge/${name}.html`);
  assert.equal(await page.locator('nav[aria-label=Primary] a[aria-current=page]').count(),1,name);
  assert.equal(await page.locator('nav[aria-label=Primary] a').count(),8,name);
 }
 report.navigation='Eight primary sections present; current section marked with aria-current on each hub page';
 await page.goto(`${root}/pages/docs/knowledge/tutorials.html`);
 await page.locator('#site-q').fill('How do I recover a database?');await page.locator('#site-q').press('Enter');
 await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('results.'));
 assert.ok((await page.locator('#results a').evaluateAll(a=>a.slice(0,5).map(x=>x.getAttribute('href')))).includes('pages/docs/knowledge/recovery.html'));
 report.siteSearch='Header search on a content page submits to the home page and returns results';
 const curated=JSON.parse(fs.readFileSync('dist/docs/search-index.json')).filter(p=>p.metadata).map(p=>p.url);
 for(const url of ['',...curated]){
  await page.goto(`${root}/${url}`);
  await page.addScriptTag({path:new URL('../node_modules/axe-core/axe.min.js',import.meta.url).pathname});
  const result=await page.evaluate(async()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}}));
  report.pages.push({url:url||'index.html',violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),incomplete:result.incomplete.map(v=>v.id)});
 }
 await page.setViewportSize({width:320,height:700});await page.goto(root);await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('results.'));
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 const overflow=[];
 for(const name of sections){await page.goto(`${root}/pages/docs/knowledge/${name}.html`);if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))overflow.push(name);}
 assert.deepEqual(overflow,[],'320px overflow on '+overflow.join(','));
 report.mobile='320px: no horizontal page overflow on the homepage and '+sections.length+' hub pages';
 await page.goto(root);await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('results.'));
 await page.screenshot({path:'dist/docs/portal-mobile.png',fullPage:false});
 await page.setViewportSize({width:1280,height:900});await page.goto(root);await page.screenshot({path:'dist/docs/portal-desktop.png',fullPage:false});
 await page.route('**/search-index.json',r=>r.abort());await page.reload();await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('could not load'));report.errorState='Search load failure exposes catalog fallback';
 fs.writeFileSync('dist/docs/accessibility-report.json',JSON.stringify(report,null,2));
 assert.equal(report.pages.flatMap(p=>p.violations).length,0,JSON.stringify(report.pages.filter(p=>p.violations.length)));
 console.log(JSON.stringify({pages:report.pages.length,axeViolations:0,incompleteRules:[...new Set(report.pages.flatMap(p=>p.incomplete))],keyboard:report.keyboard,queries:report.queries.length,navigation:report.navigation,siteSearch:report.siteSearch,levelFilter:report.levelFilter,mobile:report.mobile}));
}finally{await browser.close();}
