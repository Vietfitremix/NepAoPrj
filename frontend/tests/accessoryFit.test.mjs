import test from 'node:test';
import assert from 'node:assert/strict';
import {accessoryTarget,fitAccessory,measureAccessoryAnchors,nonLaGeometry} from '../src/utils/accessoryFit.ts';
import {getWardrobe} from '../src/utils/maleWardrobe.ts';
import {renderMaleCharacter} from '../src/utils/renderMaleCharacter.ts';
import {directionalGarmentFile,characterBaseFile} from '../src/utils/characterViews.ts';
const anchors={
  head:{x:435,y:37,width:156,height:178},neck:{x:471,y:225,width:83,height:15},
  shoulders:{x:340,y:300,width:344,height:1},waist:{x:410,y:660,width:204,height:1},
  hands:[{x:253,y:728,width:63,height:135},{x:710,y:728,width:60,height:135}],
  wrists:[{x:260,y:728,width:42,height:16},{x:720,y:728,width:32,height:16}],
};
const item=id=>getWardrobe('female').accessories.find(item=>item.id===id);
test('every accessory has finite geometry for both characters in all four views',()=>{
  for(const gender of ['male','female'])for(const accessory of getWardrobe(gender).accessories)
    for(const view of ['front','left','right','back']){
      const a=structuredClone(anchors);
      if(view==='left'||view==='right'){a.hands=[a.hands[0]];a.wrists=[a.wrists[0]];}
      const target=accessoryTarget(accessory,a,view,1.5);
      assert.ok(Object.values(target).every(Number.isFinite),accessory.id+'/'+view);
      assert.ok(target.width>0&&target.height>0);
    }
});
test('headwear brims stay above the eyes and glasses stay centred on the face',()=>{
  const hat=accessoryTarget(item('non-la'),anchors,'front',1.15);
  const glasses=accessoryTarget(item('kinh-ram'),anchors,'front',3.25);
  assert.ok(hat.y+hat.height*.63<glasses.y);
  assert.equal(glasses.x+glasses.width/2,anchors.head.x+anchors.head.width/2);
  const wrap=accessoryTarget(item('khan-xep'),anchors,'front',1.5);
  assert.ok(wrap.y+wrap.height<glasses.y);
});
test('cap and wrap crowns fit the skull even when the source sprite is vertically stretched',()=>{
  for(const view of ['front','left','right','back'])for(const id of ['mu-luoi-trai','mu-cao-boi','khan-van','khan-xep']){
    const a=accessoryTarget(item(id),anchors,view,.6),b=accessoryTarget(item(id),anchors,view,2.5);
    assert.deepEqual(a,b,id+'/'+view);
    assert.ok(a.height<=anchors.head.height*.6);
    assert.ok(a.y+a.height<anchors.head.y+anchors.head.height*.4);
    if(id==='mu-luoi-trai')assert.ok(a.width<=anchors.head.width*1.18);
  }
});
test('conical hats keep their crown shape, seat on the head, and let the strap hang below the chin',()=>{
  const crownCrop={x:315,y:99,width:395,height:240};
  for(const view of ['front','left','right','back']){
    const a=nonLaGeometry(anchors,view,crownCrop,{x:350,y:220,width:320,height:221});
    const b=nonLaGeometry(anchors,view,crownCrop,{x:350,y:220,width:320,height:400});
    assert.deepEqual(a.crown,b.crown,'strap length cannot stretch the crown');
    assert.ok(Math.abs(a.crown.width/a.crown.height-crownCrop.width/crownCrop.height)<1e-8);
    const brim=a.crown.y+a.crown.height;
    assert.ok(brim>anchors.head.y&&brim<anchors.head.y+anchors.head.height*.4);
    assert.ok(a.strap.y+a.strap.height>anchors.head.y+anchors.head.height);
    if(view!=='back')assert.ok(a.strap.y+a.strap.height>=anchors.head.y+anchors.head.height*1.2);
    if(view==='left')assert.ok(a.chinX<anchors.head.x+anchors.head.width/2);
    if(view==='right')assert.ok(a.chinX>anchors.head.x+anchors.head.width/2);
  }
});
test('a profile jaw cannot shift or enlarge the necklace anchor',()=>{
  const pixels=new Uint8ClampedArray(1024*1536*4);
  const fill=(x0,x1,y0,y1)=>{for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){
    const i=(y*1024+x)*4;pixels.set([205,150,110,255],i);
  }};
  fill(430,580,30,215);fill(410,565,215,236);fill(484,560,240,256);
  const original=globalThis.document;
  globalThis.document={createElement:()=>({getContext:()=>({drawImage(){},getImageData:()=>({data:pixels})})})};
  try{
    const measured=measureAccessoryAnchors({width:1024,height:1536},'female','left');
    assert.equal(measured.neck.x,484);assert.equal(measured.neck.width,76);
    const necklace=accessoryTarget(item('kieng-bac'),measured,'left',1);
    assert.ok(necklace.x>=480&&necklace.x+necklace.width<=565);
  }finally{if(original===undefined)delete globalThis.document;else globalThis.document=original;}
});
test('wrist accessories fit each hand independently and held bags reach the fingers',()=>{
  const bracelet=accessoryTarget(item('vong-tay'),anchors,'front',2.5);
  assert.ok(bracelet.x<=anchors.wrists[1].x);
  assert.ok(bracelet.x+bracelet.width>=anchors.wrists[1].x+anchors.wrists[1].width);
  const glove0=accessoryTarget(item('gang-tay-ho-ngon'),anchors,'front',1,0);
  const glove1=accessoryTarget(item('gang-tay-ho-ngon'),anchors,'front',1,1);
  assert.notEqual(glove0.width,glove1.width);
  for(const view of ['front','back']){
    const bag=accessoryTarget(item('tui-coi'),anchors,view,.8),hand=anchors.hands[view==='back'?0:1];
    assert.equal(bag.x+bag.width/2,hand.x+hand.width/2);
    assert.ok(bag.y>hand.y&&bag.y<hand.y+hand.height);
  }
});
test('accessories follow changes in body size and position',()=>{
  const scaled=Object.fromEntries(Object.entries(anchors).map(([key,value])=>{
    const scale=b=>({x:b.x*.8+20,y:b.y*.8+10,width:b.width*.8,height:b.height*.8});
    return [key,Array.isArray(value)?value.map(scale):scale(value)];
  }));
  for(const id of ['non-la','kinh-ram','bong-tai','hoa-cai-toc','tui-coi','quat-giay']){
    const original=accessoryTarget(item(id),anchors,'front',1.5);
    const resized=accessoryTarget(item(id),scaled,'front',1.5);
    assert.ok(Math.abs(resized.width-original.width*.8)<1e-8,id);
    assert.ok(Math.abs(resized.x-(original.x*.8+20))<1e-8,id);
    assert.ok(Math.abs(resized.y-(original.y*.8+10))<1e-8,id);
  }
});
test('rendering without a raster environment preserves existing source layers',()=>{
  const image={file:'hat'},body={file:'body'};
  assert.deepEqual(fitAccessory(image,body,item('non-la'),'female','front'),{image,offsetX:0,offsetY:-200});
});
test('charms attach to the current carrier at the bag edge in each view',()=>{
  for(const id of ['tui-coi','tui-tote','tui-deo-cheo','ba-lo'])for(const view of ['front','left','right','back']){
    const carrier=item(id),target=accessoryTarget(carrier,anchors,view,.8);
    const charm=accessoryTarget(item('moc-khoa-bong'),anchors,view,.67,0,{target,id,slot:carrier.slot});
    const attachment=charm.x+charm.width/2;
    assert.ok(attachment>target.x&&attachment<target.x+target.width,id+'/'+view);
    assert.ok(charm.y>=target.y&&charm.y<target.y+target.height,id+'/'+view);
    const moved=accessoryTarget(item('moc-khoa-bong'),anchors,view,.67,0,
      {target:{...target,x:target.x+37,y:target.y-19},id,slot:carrier.slot});
    assert.ok(Math.abs(moved.x-charm.x-37)<1e-8);assert.ok(Math.abs(moved.y-charm.y+19)<1e-8);
  }
});
test('a charm behind the body is occluded together with its carrier',()=>{
  for(const [id,slot,view,rear] of [['tui-deo-cheo','bag','left',true],['ba-lo','backpack','right',true],
    ['tui-coi','bag','left',false],['ba-lo','backpack','back',false]]){
    const carrier=item(id),charm=item('moc-khoa-bong'),base=characterBaseFile('female',view);
    const carrierFile=directionalGarmentFile(carrier.file,view),charmFile=directionalGarmentFile(charm.file,view);
    const images=Object.fromEntries([base,carrierFile,charmFile].map(file=>[file,{file}]));
    const drawn=[],noop=()=>{},ctx={clearRect:noop,save:noop,restore:noop,translate:noop,
      beginPath:noop,rect:noop,clip:noop,drawImage:image=>drawn.push(image.file)};
    renderMaleCharacter(ctx,images,{shirt:null,pants:null,accessories:{[slot]:id,bagCharm:charm.id}},'female',view);
    assert.equal(drawn.indexOf(charmFile)<drawn.indexOf(base),rear,id+'/'+view);
  }
});
