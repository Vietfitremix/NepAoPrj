import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import { characterViews, normalizeView, rotateView, characterBaseFile } from '../src/utils/characterViews.ts';

test('four quarter turns return to the front in either direction', () => {
  assert.deepEqual(characterViews.map(view=>view.angle), [0,90,180,270]);
  for(const step of [-1,1]){
    let view='front';const visited=new Set();
    for(let i=0;i<4;i++){visited.add(view);view=rotateView(view,step);}
    assert.equal(visited.size,4);assert.equal(view,'front');
  }
  assert.equal(rotateView('front',-1),'left');
  assert.equal(rotateView('left',1),'front');
});

test('each non-front direction has a dedicated image and invalid storage resets',()=>{
  assert.equal(normalizeView('back'),'back');
  for(const bad of [null,undefined,'side',90,{}])assert.equal(normalizeView(bad),'front');
  for(const gender of ['male','female']){
    const files=characterViews.map(view=>characterBaseFile(gender,view.id));
    assert.equal(new Set(files).size,4);
    assert.ok(files.every(file=>file.startsWith('body/')));
    for(const file of files)assert.ok(existsSync(new URL('../public/figure/'+gender+'-layers/'+file,import.meta.url)),file);
  }
});
