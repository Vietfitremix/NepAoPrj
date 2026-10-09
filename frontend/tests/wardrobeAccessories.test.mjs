import test from 'node:test';
import assert from 'node:assert/strict';
import {getWardrobe,normalizeMaleSelection,readMaleSelection,selectedAccessories,selectedWardrobeItems,accessorySlots} from '../src/utils/maleWardrobe.ts';
import {renderMaleCharacter,characterHeadroom} from '../src/utils/renderMaleCharacter.ts';
import {directionalGarmentFile,characterBaseFile} from '../src/utils/characterViews.ts';
import {colorizePixels,normalizeGarmentStyles,wardrobePatterns} from '../src/utils/wardrobeStyles.ts';

test('accessories, colours and patterns survive storage and rotation while clothes change',()=>{
 for(const gender of ['male','female']){
  const c=getWardrobe(gender),accessories=Object.fromEntries(accessorySlots.map(({id})=>[id,c.accessories.find(item=>item.slot===id).id]));
  const selection={shirt:c.outfits[0].id,pants:c.pants[0].id,shoes:'giay-the-thao',accessories,styles:{shirt:{color:'#B52838',pattern:'canh-dao-xuan'},pants:{color:'#24242a',pattern:null},shoes:{color:'#32679e',pattern:null}}};
  const normalized=readMaleSelection(JSON.stringify(selection),gender);
  assert.equal(normalized.styles.shirt.color,'#b52838');assert.deepEqual(normalized.accessories,accessories);
  const replaced=normalizeMaleSelection({...normalized,shirt:c.outfits[1].id},gender);
  assert.deepEqual(replaced.styles,normalized.styles);assert.deepEqual(replaced.accessories,accessories);
  assert.equal(selectedAccessories(replaced,gender).length,accessorySlots.length);
  for(const view of ['front','left','right','back']){
   const files=selectedWardrobeItems(replaced,gender).map(item=>directionalGarmentFile(item.file,view));
   // Test layer order with original texture; style pixels are checked separately.
   const drawn=[],translations=[],noop=()=>{},images=Object.fromEntries(files.map(file=>[file,{file}]));
   const base=characterBaseFile(gender,view),hand=`views/hands-${view}.png`;images[base]={file:base};images[hand]={file:hand};
   const context={clearRect:noop,save:noop,restore:noop,translate:(x,y)=>translations.push([x,y]),beginPath:noop,closePath:noop,moveTo:noop,lineTo:noop,rect:noop,clip:noop,drawImage:image=>drawn.push(image.file)};
   const before=structuredClone(replaced);renderMaleCharacter(context,images,{...replaced,styles:{}},gender,view);
   assert.deepEqual([...new Set(drawn.filter(file=>files.includes(file)))].sort(),files.sort());
   assert.ok(translations.some(([x,y])=>x===0&&y===characterHeadroom));
   for(const slot of ['bag','fan']){const item=c.accessories.find(item=>item.id===accessories[slot]);assert.ok(drawn.indexOf(directionalGarmentFile(item.file,view))<drawn.indexOf(hand));}
   assert.deepEqual(replaced,before);
  }
 }
});

test('invalid or wrong-slot accessories and malformed styles recover independently',()=>{
 const saved={shirt:null,pants:null,shoes:null,accessories:{headwear:'tui-coi',bag:'non-la',fan:'missing',earrings:'bong-tai',unknown:'anything'},styles:{shirt:{color:'red',pattern:'missing'},pants:{color:'#ABCDEF',pattern:'hoa-cuc'},shoes:[]}};
 const value=normalizeMaleSelection(saved,'female');assert.equal(value.accessories.earrings,'bong-tai');assert.equal(value.accessories.headwear,null);assert.equal(value.accessories.bag,null);assert.ok(!('unknown' in value.accessories));
 assert.deepEqual(value.styles,{shirt:{color:null,pattern:null},pants:{color:'#abcdef',pattern:'hoa-cuc'}});
 assert.deepEqual(normalizeGarmentStyles([]),{});assert.equal(wardrobePatterns.length,18);
});

test('recolouring preserves alpha and fabric light/shadow contrast',()=>{
 const data=new Uint8ClampedArray([50,50,50,255,200,200,200,128,20,30,40,0]);
 colorizePixels(data,'#b52838');assert.equal(data[3],255);assert.equal(data[7],128);assert.deepEqual([...data.slice(8)],[20,30,40,0]);
 assert.ok(data[0]<data[4]);assert.ok(data[1]<data[5]);assert.ok(data[2]<data[6]);assert.ok(data[0]>data[1]);
 const before=[...data];colorizePixels(data,'invalid');assert.deepEqual([...data],before);
});

test('closed shoes replace exposed soles while open clogs retain the original feet',()=>{
 for(const gender of ['male','female'])for(const view of ['front','left','right','back']){
  const original=characterBaseFile(gender,view),bottom=`views/base-bottom-${view}.png`,covered=`views/base-bottom-shoes-${view}.png`;
  const images=Object.fromEntries([original,bottom,covered].map(file=>[file,{file}])),drawn=[],noop=()=>{};
  const context={clearRect:noop,save:noop,restore:noop,translate:noop,beginPath:noop,closePath:noop,moveTo:noop,lineTo:noop,clip:noop,drawImage:image=>drawn.push(image.file)};
  renderMaleCharacter(context,images,{shirt:null,pants:'ivory',shoes:'hai-theu'},gender,view);assert.equal(drawn[0],covered);
  drawn.length=0;renderMaleCharacter(context,images,{shirt:null,pants:'ivory',shoes:'guoc'},gender,view);assert.equal(drawn[0],bottom);
 }
});
