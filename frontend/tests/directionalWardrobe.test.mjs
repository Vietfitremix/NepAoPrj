import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { getWardrobe } from '../src/utils/maleWardrobe.ts';
import { characterBaseFile, directionalGarmentFile, rotateView } from '../src/utils/characterViews.ts';
import { renderMaleCharacter } from '../src/utils/renderMaleCharacter.ts';

test('changing directions retains each selected item independently, including removals', () => {
  for (const character of ['male', 'female']) {
    const catalog = getWardrobe(character);
    const items = [...catalog.outfits, ...catalog.pants, ...catalog.shoes];
    for (const view of ['front','left','right','back']) {
      const files = [characterBaseFile(character,view), `views/hands-${view}.png`, ...items.map(item => directionalGarmentFile(item.file,view))];
      const images = Object.fromEntries(files.map(file => [file,{file}]));
      for (const shirt of [null,...catalog.outfits.map(item => item.id)])
        for (const pants of [null,...catalog.pants.map(item => item.id)])
          for (const shoes of [null,...catalog.shoes.map(item => item.id)]) {
            const selection = {shirt,pants,shoes}, before = {...selection}, drawn = [];
            const noop = () => {};
            const context = {clearRect:noop,save:noop,restore:noop,translate:noop,scale:noop,
              beginPath:noop,closePath:noop,moveTo:noop,lineTo:noop,rect:noop,clip:noop,
              drawImage: image => drawn.push(image.file)};
            renderMaleCharacter(context,images,selection,character,view);
            const expected = [catalog.outfits.find(item => item.id===shirt),catalog.pants.find(item => item.id===pants),catalog.shoes.find(item => item.id===shoes)]
              .filter(Boolean).map(item => directionalGarmentFile(item.file,view)).sort();
            assert.deepEqual([...new Set(drawn.filter(file => /^(shirts|pants|skirts|shoes)\//.test(file)))].sort(), expected);
            assert.equal(drawn[0], characterBaseFile(character,view));
            assert.deepEqual(selection,before);
            assert.equal(rotateView(rotateView(view,1),-1),view);
          }
    }
  }
});

test('every selectable item has four independent full-canvas RGBA source layers', () => {
  let count = 0;
  for (const character of ['male','female']) {
    const catalog = getWardrobe(character);
    for (const item of [...catalog.outfits,...catalog.pants,...catalog.shoes,...catalog.accessories]) {
      const files = ['front','right','left','back'].map(view => directionalGarmentFile(item.file,view));
      assert.equal(new Set(files).size,4);
      const hashes = new Set();
      for (const file of files) {
        const png = readFileSync(new URL(`../public/figure/${character}-layers/${file}`,import.meta.url));
        assert.equal(png.subarray(1,4).toString(),'PNG',file);
        assert.equal(png.readUInt32BE(16),1024,file);
        assert.equal(png.readUInt32BE(20),1536,file);
        assert.equal(png[25],6,file);
        hashes.add(createHash('sha256').update(png).digest('hex'));
        count++;
      }
      assert.equal(hashes.size,4,`${character}/${item.id} must have four distinct rendered directions`);
    }
  }
  assert.equal(count,300);
});

test('the new male and female bottoms remain selectable through saved selections', async () => {
  const {normalizeMaleSelection,readMaleSelection} = await import('../src/utils/maleWardrobe.ts');
  const expected={male:['long-navy','shorts-khaki','cropped-olive','slim-black','wide-charcoal'],female:['skirt-short-navy','skirt-long-ivory','shorts-denim','long-black']};
  for(const character of ['male','female'])for(const pants of expected[character]){
    assert.ok(getWardrobe(character).pants.some(item=>item.id===pants));
    const selection={shirt:null,pants,shoes:null};
    assert.deepEqual(normalizeMaleSelection(selection,character),selection);
    assert.deepEqual(readMaleSelection(JSON.stringify(selection),character),selection);
  }
});

test('a selected bottom uses the prepared body while removal restores the original base', () => {
  for(const character of ['male','female'])for(const view of ['front','left','right','back']){
    const original=characterBaseFile(character,view),prepared=`views/base-bottom-${view}.png`;
    const images={[original]:{file:original},[prepared]:{file:prepared}};
    const drawn=[],noop=()=>{},context={clearRect:noop,save:noop,restore:noop,translate:noop,beginPath:noop,closePath:noop,moveTo:noop,lineTo:noop,clip:noop,drawImage:image=>drawn.push(image.file)};
    renderMaleCharacter(context,images,{shirt:null,pants:'ivory',shoes:null},character,view);
    assert.equal(drawn[0],prepared);
    drawn.length=0;
    renderMaleCharacter(context,images,{shirt:null,pants:null,shoes:null},character,view);
    assert.equal(drawn[0],original);
  }
});
