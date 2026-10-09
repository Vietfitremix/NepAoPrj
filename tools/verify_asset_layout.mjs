import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,access} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),views=['front','left','right','back'];
const file=relative=>path.join(root,relative);let count=0,sourceCount=0;
for(const gender of ['male','female']){
 const publicRoot=`frontend/public/figure/${gender}-layers`,catalog=JSON.parse(await readFile(file(`${publicRoot}/catalog.json`),'utf8'));
 assert.equal(catalog.base,'body/front.png');for(const view of views)await access(file(`${publicRoot}/body/${view}.png`));
 for(const kind of ['outfits','pants','shoes','accessories'])for(const item of catalog[kind]){
  const expected=kind==='accessories'?item.category:kind==='outfits'?'shirts':kind==='shoes'?'shoes':item.id.startsWith('skirt-')?'skirts':'pants';
  assert.equal(item.category,expected);assert.equal(item.file,`${expected}/${item.id}/front.png`);
  await access(file(`${publicRoot}/${item.thumbnail}`));await access(file(item.reference));
  const hashes=new Set();for(const view of views){
   const image=await readFile(file(`${publicRoot}/${expected}/${item.id}/${view}.png`));
   assert.equal(image.readUInt32BE(16),1024);assert.equal(image.readUInt32BE(20),1536);assert.equal(image[25],6);hashes.add(createHash('sha256').update(image).digest('hex'));count++;
   if(view==='front'&&!item.sourcePrepared)continue;
   const metadata=JSON.parse(await readFile(file(`assets/wardrobe/${gender}/${expected}/${item.id}/source/${view}.json`),'utf8'));
   await access(file(metadata.file));for(const input of metadata.inputs)await access(path.isAbsolute(input)?input:file(input));sourceCount++;
  }
  assert.equal(hashes.size,4);
 }
}
const migration=JSON.parse(await readFile(file('assets/metadata/path-migration.json'),'utf8'));
for(const {file:relative,hash} of migration.spriteHashes)assert.equal(createHash('sha256').update(await readFile(file(relative))).digest('hex'),hash,relative);
assert.equal(count,344);assert.equal(sourceCount,325);
const patterns=JSON.parse(await readFile(file('frontend/public/figure/patterns/catalog.json'),'utf8'));assert.equal(patterns.length,18);
for(const item of patterns){for(const relative of [item.file,item.thumbnail])await access(file('frontend/public/figure/'+relative));
 const png=await readFile(file('frontend/public/figure/'+item.file));assert.equal(png[25],6);
 const metadata=JSON.parse(await readFile(file(`assets/patterns/${item.id}/source/tile.json`),'utf8'));await access(file(metadata.file));}
console.log(`Verified ${count} categorized sprites, ${sourceCount} source/prompt pairs, and all original sprite hashes.`);
