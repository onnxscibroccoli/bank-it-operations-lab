import test from 'node:test';
import assert from 'node:assert/strict';
import {drawSnapshot,seededRandom} from '../ambient-backdrop.js';

function fakeCanvas() {
  const calls=[];
  const ctx=new Proxy({},{
    get(target,key) {
      if (key==='clearRect'||key==='beginPath'||key==='arc'||key==='fill'
        ||key==='moveTo'||key==='lineTo'||key==='stroke')
        return (...args)=>calls.push([key,...args]);
      return target[key];
    },
    set(target,key,value) {
      if (key==='fillStyle'||key==='strokeStyle'||key==='lineWidth')
        calls.push([key,value]);
      target[key]=value;
      return true;
    }
  });
  return {calls,canvas:{width:0,height:0,getContext:()=>ctx}};
}

test('same seed and viewport generate identical static geometry',()=>{
  const left=fakeCanvas(),right=fakeCanvas();
  assert.equal(drawSnapshot(left.canvas,123456,480,360),true);
  assert.equal(drawSnapshot(right.canvas,123456,480,360),true);
  assert.deepEqual(left.calls,right.calls);
  assert.equal(left.canvas.width,480);
  assert.equal(left.canvas.height,360);
});

test('different seeds produce different snapshots',()=>{
  const a=fakeCanvas(),b=fakeCanvas();
  drawSnapshot(a.canvas,1,320,240);
  drawSnapshot(b.canvas,2,320,240);
  assert.notDeepEqual(a.calls.slice(0,100),b.calls.slice(0,100));
});

test('seeded PRNG stays in [0,1) and is reproducible',()=>{
  const x=seededRandom(17),y=seededRandom(17);
  for(let i=0;i<50;i++){
    const v=x();
    assert.ok(v>=0 && v<1);
    assert.equal(v,y());
  }
});

test('canvas work is bounded and unavailable context degrades gracefully',()=>{
  const a=fakeCanvas();
  drawSnapshot(a.canvas,99,99999,99999);
  assert.equal(a.canvas.width,1400);
  assert.equal(a.canvas.height,900);
  assert.equal(drawSnapshot({getContext:()=>null},99,320,240),false);
});
