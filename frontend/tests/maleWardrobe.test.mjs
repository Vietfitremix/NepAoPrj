import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {getWardrobe, maleLayers, normalizeMaleSelection, readMaleSelection, selectionKey} from '../src/utils/maleWardrobe.ts';
import {fittedShirtMesh,fitBodyPoint} from '../src/utils/renderMaleCharacter.ts';

test('both wardrobes contain all five garment families and separate asset roots',()=>{
 for(const gender of ['male','female']){
  const c=getWardrobe(gender);
  for(const id of ['tu-than','ngu-than','nhat-binh','ba-ba'])assert.ok(c.outfits.some(x=>x.id===id));
  assert.ok(c.outfits.some(x=>['navy','jade'].includes(x.id)));
  for(const file of [c.base,...c.outfits.map(x=>x.file),...c.pants.map(x=>x.file),...c.shoes.map(x=>x.file)])
   assert.ok(existsSync(new URL('../public/figure/'+gender+'-layers/'+file,import.meta.url)),file);
 }
 assert.notEqual(selectionKey('male'),selectionKey('female'));
 assert.equal(normalizeMaleSelection({shirt:'navy'},'female').shirt,'jade');
 assert.equal(normalizeMaleSelection({shirt:'jade'},'male').shirt,'navy');
});

test('shirt, pants and footwear are independent; bases are barefoot',()=>{
 for(const gender of ['male','female']){
  const c=getWardrobe(gender);
  assert.equal(maleLayers({shirt:null,pants:null,shoes:null},gender).length,1);
  const selected={shirt:c.outfits[0].id,pants:'ivory',shoes:c.shoes[0].id};
  assert.equal(normalizeMaleSelection({...selected,shirt:null},gender).shoes,c.shoes[0].id);
  assert.equal(normalizeMaleSelection({...selected,shoes:null},gender).shirt,selected.shirt);
  assert.deepEqual(maleLayers(selected,gender).map(x=>x.file),[c.base,c.pants[0].file,c.outfits[0].file]);
  for(const shoes of c.shoes)for(const crop of shoes.crops){
   assert.ok(crop[0]>=0&&crop[1]>=0&&crop[2]>0&&crop[3]>0);
   assert.ok(crop[0]+crop[2]<=1024&&crop[1]+crop[3]<=1536);
  }
 }
});

test('saved older outfits migrate and invalid values recover without shoes',()=>{
 assert.deepEqual(readMaleSelection('base'),{shirt:null,pants:null,shoes:null});
 assert.deepEqual(readMaleSelection('teal'),{shirt:'teal',pants:'ivory',shoes:null});
 assert.deepEqual(readMaleSelection('{"shirt":"burgundy","pants":null}'),{shirt:'burgundy',pants:null,shoes:null});
 for(const raw of [null,'invalid-json','42','{}'])
  assert.deepEqual(readMaleSelection(raw),{shirt:'navy',pants:'ivory',shoes:null});
 assert.deepEqual(readMaleSelection('{"shirt":null,"pants":null,"shoes":"bad"}','female'),{shirt:null,pants:null,shoes:null});
});

test('every fitted garment keeps a finite mesh without inverted triangles',()=>{
 for(const gender of ['male','female'])for(const outfit of getWardrobe(gender).outfits){
  const layer=maleLayers({shirt:outfit.id,pants:null},gender)[1];
  for(const {target} of fittedShirtMesh(layer,gender)){
   const [a,b,c]=target;
   assert.ok(target.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)));
   assert.ok((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)>0,gender+' '+outfit.id);
  }
 }
});

test('dedicated garments align elbow and wrist centers with each avatar',()=>{
 const centers={male:{550:297,725:239.5},female:{550:348.5,725:297.5}};
 for(const gender of ['male','female'])for(const outfit of getWardrobe(gender).outfits){
  if(!outfit.fitRows)continue;
  for(const y of [550,725]){
   const row=outfit.fitRows.find(row=>row.y===y);
   assert.equal(row.points.length,5);
   const sourceCenter=(row.points[1][0]+row.points[2][0])/2;
   const point=fitBodyPoint({x:sourceCenter,y},outfit.fitRows);
   assert.ok(Math.abs(point.x-centers[gender][y])<6,gender+' '+outfit.id+' '+y);
   const mirror=fitBodyPoint({x:1024-sourceCenter,y},outfit.fitRows);
   assert.ok(Math.abs(point.x+mirror.x-1024)<1e-6);
  }
 }
});
