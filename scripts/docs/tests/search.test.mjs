import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {search} from '../search-core.js';
const pages=JSON.parse(fs.readFileSync('dist/docs/search-index.json','utf8'));
export const cases=[
 ['How do backups work?','recovery'],['What happens when a database crashes?','recovery'],
 ['What does least privilege mean?','identity'],['How do I control employee permissions?','identity'],
 ['How can a company recover from a cyberattack?','recovery'],['What is infrastructure as code?','infrastructure'],
 ['How do IT departments detect outages?','incident'],['How do I investigate why a service stopped working?','incident'],
 ['What is the difference between authentication and authorization?','identity'],['How do I automate routine IT maintenance?','infrastructure']
];
for(const [query,id] of cases)test(query,()=>assert.ok(search(pages,query).slice(0,5).some(p=>p.id===id)));
test('unknown query produces no matches',()=>assert.equal(search(pages,'zzzxnonexistentzz').length,0));
test('category filter excludes unrelated records',()=>assert.ok(search(pages,'access','identity-access').every(p=>p.category==='identity-access')));
test('status filter excludes other maturity labels',()=>assert.ok(search(pages,'recovery','','In Development').every(p=>p.status==='In Development')));
test('no query browses all indexed documents',()=>assert.equal(search(pages,'').length,pages.length));
