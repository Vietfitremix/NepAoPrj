import test from 'node:test';
import assert from 'node:assert/strict';
import { configureWardrobe, initialWardrobe } from '../src/utils/mixWardrobe.ts';
import { outfitPreview } from '../src/utils/outfitPreview.ts';
import { applyChanges } from '../src/utils/mix.ts';
import { getWardrobe, normalizeMaleSelection } from '../src/utils/maleWardrobe.ts';
import { selection as apiSelection } from '../src/services/backendContract.ts';

const config={conceptId:'c1',outfitCode:'AO_DAI',colorCode:'RED',styleCode:'GEN_Z',eventCode:'TET',accessoryCodes:[]};
const outfits=['AO_DAI','AO_TU_THAN','AO_NGU_THAN','NHAT_BINH','AO_BA_BA'].map(code=>({code,
  colors:[{code:'RED',hex:'#b52838'},{code:'BLUE',hex:'#32679e'}],
  accessories:['NON_LA','QUAN_LUA','TRANG_SUC','WHITE_SNEAKERS','MINIMAL_BAG'].map(code=>({code}))}));

test('every existing garment and modern accessory remains selectable and survives JSON storage',()=>{
  for(const character of ['male','female']){
    const catalog=getWardrobe(character);
    for(const shirt of catalog.outfits)for(const accessory of catalog.accessories){
      const raw={shirt:shirt.id,pants:catalog.pants.at(-1).id,shoes:'dep-crocs',
        accessories:{[accessory.slot]:accessory.id},styles:{shirt:{color:'#765a94',pattern:'cham-bi'}}};
      const value=configureWardrobe(config,raw,character,outfits);
      const saved=JSON.parse(JSON.stringify(value));
      assert.deepEqual(outfitPreview(saved),normalizeMaleSelection(raw,character));
      assert.equal(saved.wardrobe.selection.shirt,shirt.id);
      assert.ok(value.accessoryCodes.every(code=>outfits.find(o=>o.code===value.outfitCode).accessories.some(a=>a.code===code)));
    }
  }
});

test('AI remix updates visible colors and known accessories while retaining modern pieces and patterns',()=>{
  const original=configureWardrobe(config,{shirt:'navy',pants:'long-navy',shoes:'dep-crocs',
    accessories:{headwear:'non-la',headphones:'tai-nghe',bag:'tui-tote'},styles:{shirt:{pattern:'cham-bi'}}},'male',outfits);
  const next=applyChanges(original,{colorCode:'BLUE',removeAccessories:['NON_LA'],addAccessories:['WHITE_SNEAKERS']});
  assert.equal(next.wardrobe.selection.styles.shirt.color,'#32679e');
  assert.equal(next.wardrobe.selection.styles.shirt.pattern,'cham-bi');
  assert.equal(next.wardrobe.selection.accessories.headphones,'tai-nghe');
  assert.equal(next.wardrobe.selection.accessories.bag,'tui-tote');
  assert.equal(next.wardrobe.selection.accessories.headwear,null);
  assert.equal(next.wardrobe.selection.shoes,'sneakers');
  assert.equal(original.wardrobe.selection.accessories.headwear,'non-la');
});

test('male context initializes a male outfit and changing garment filters unsupported API accessories',()=>{
  assert.equal(initialWardrobe(config,'male').selection.shirt,'navy');
  const limited=[...outfits.filter(o=>o.code!=='NHAT_BINH'),{...outfits[3],accessories:[]}];
  const next=configureWardrobe(config,{shirt:'nhat-binh',pants:'ivory',shoes:'sneakers',accessories:{headwear:'non-la',glasses:'kinh-ram'}},'female',limited);
  assert.equal(next.outfitCode,'NHAT_BINH');assert.deepEqual(next.accessoryCodes,[]);
  assert.equal(next.wardrobe.selection.accessories.glasses,'kinh-ram');
});

test('custom colors and modern accessories reach the cultural check and saved look contract',()=>{
  const next=configureWardrobe(config,{shirt:'jade',pants:'ivory',shoes:'dep-crocs',
    accessories:{headphones:'tai-nghe'},styles:{shirt:{color:'#315f92'}}},'female',outfits);
  assert.equal(next.colorCode,'BLUE');
  assert.equal(apiSelection(next).wardrobe.selection.styles.shirt.color,'#315f92');
  assert.equal(apiSelection(next).wardrobe.selection.shoes,'dep-crocs');
  assert.equal(apiSelection(next).wardrobe.selection.accessories.headphones,'tai-nghe');
});
