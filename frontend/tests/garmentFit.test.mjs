import test from 'node:test';
import assert from 'node:assert/strict';
import {sourceRow} from '../src/utils/garmentFit.ts';
import {leftGarmentSourceFile} from '../src/utils/characterViews.ts';
import {getWardrobe} from '../src/utils/maleWardrobe.ts';
import {readFileSync} from 'node:fs';

test('continuous garment fitting keeps rows ordered and avoids band boundaries',()=>{
 const stops=[[224,108],[302,242],[735,830],[1190,1450]];
 for(const [target,source] of stops)assert.equal(sourceRow(target,stops),source);
 let previous=sourceRow(224,stops);
 for(let y=224.25;y<=1190;y+=.25){const next=sourceRow(y,stops);assert.ok(next>=previous);assert.ok(Number.isFinite(next));previous=next;}
 for(const [y] of stops.slice(1,-1)){
  const before=(sourceRow(y,stops)-sourceRow(y-.01,stops))/.01;
  const after=(sourceRow(y+.01,stops)-sourceRow(y,stops))/.01;
  assert.ok(Math.abs(before-after)<.001,'shoulder and cuff derivatives stay continuous');
 }
});

test('row interpolation remains finite at flat sections and turning points',()=>{
 for(const stops of [
  [[0,10],[20,10],[40,30],[60,30]],
  [[0,10],[20,30],[40,10]],
 ]){
  for(let y=0;y<=stops.at(-1)[0];y+=.25){
   const value=sourceRow(y,stops);
   assert.ok(Number.isFinite(value));
   assert.ok(value>=10-1e-9&&value<=30+1e-9);
  }
 }
});

test('every garment uses its own existing left source through the database asset route',()=>{
 for(const character of ['male','female'])for(const item of getWardrobe(character).outfits){
  const url=leftGarmentSourceFile(item.reference);
  assert.ok(url.startsWith('/api/assets/assets/wardrobe/'+character+'/shirts/'+item.id+'/'));
  const png=readFileSync(new URL('../../'+url.replace('/api/assets/',''),import.meta.url));
  assert.equal(png.subarray(1,4).toString(),'PNG');
 }
});
