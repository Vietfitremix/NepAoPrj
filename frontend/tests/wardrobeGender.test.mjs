import test from 'node:test';
import assert from 'node:assert/strict';
import male from '../public/figure/male-layers/catalog.json' with {type:'json'};
import female from '../public/figure/female-layers/catalog.json' with {type:'json'};
import {getWardrobe,normalizeMaleSelection,setWardrobeCatalogs} from '../src/utils/maleWardrobe.ts';
import {configureWardrobe} from '../src/utils/mixWardrobe.ts';

test('gender-specific items follow the AI catalog while modern shared items remain in both wardrobes',()=>{
  const ids=(character,category)=>getWardrobe(character)[category].map(item=>item.id);
  for(const id of ['tu-than','nhat-binh']){
    assert.ok(!ids('male','outfits').includes(id));
    assert.ok(ids('female','outfits').includes(id));
  }
  for(const id of ['non-quai-thao','khan-mo-qua','hoa-cai-toc','kieng-bac','bong-tai','vong-tay']){
    assert.ok(!ids('male','accessories').includes(id));
    assert.ok(ids('female','accessories').includes(id));
  }
  assert.ok(!ids('male','shoes').includes('giay-bup-be'));
  assert.ok(!ids('female','shoes').includes('giay-ta'));
  assert.ok(!ids('female','accessories').includes('khan-xep'));
  for(const character of ['male','female']){
    for(const id of ['tai-nghe','kinh-ram','tui-tote','ba-lo'])assert.ok(ids(character,'accessories').includes(id));
    for(const category of ['outfits','pants','shoes','accessories'])
      assert.ok(getWardrobe(character)[category].every(item=>['unisex',character].includes(item.gender)));
  }
});

test('changing gender removes incompatible saved items and keeps shared accessories, colours and patterns',()=>{
  const raw={shirt:'nhat-binh',pants:'skirt-short-navy',shoes:'giay-bup-be',
    accessories:{headwear:'non-quai-thao',earrings:'bong-tai',glasses:'kinh-ram',bag:'tui-tote'},
    styles:{shirt:{color:'#765a94',pattern:'cham-bi'}}};
  const before=structuredClone(raw);
  const value=normalizeMaleSelection(raw,'male');
  assert.equal(value.shirt,'navy');assert.equal(value.pants,'ivory');assert.equal(value.shoes,null);
  assert.equal(value.accessories.headwear,null);assert.equal(value.accessories.earrings,null);
  assert.equal(value.accessories.glasses,'kinh-ram');assert.equal(value.accessories.bag,'tui-tote');
  assert.deepEqual(value.styles,raw.styles);assert.deepEqual(raw,before);
  const config={conceptId:'old',outfitCode:'NHAT_BINH',colorCode:'PURPLE',styleCode:'MINIMAL',eventCode:'TET',accessoryCodes:['NON_QUAI_THAO']};
  const normalized=configureWardrobe(config,raw,'male',[{code:'AO_DAI',colors:[{code:'PURPLE',hex:'#765a94'}],accessories:[]}]);
  assert.equal(normalized.outfitCode,'AO_DAI');assert.deepEqual(normalized.accessoryCodes,[]);
  assert.equal(normalizeMaleSelection({accessories:{headwear:'khan-xep'}},'female').accessories.headwear,null);
});

test('database catalog refresh applies gender filtering without mutating its source data',()=>{
  const catalogs=structuredClone({male,female});
  const before=structuredClone(catalogs);
  try{
    setWardrobeCatalogs(catalogs);
    assert.equal(getWardrobe('male').outfits.length,5);
    assert.equal(getWardrobe('female').accessories.length,21);
    assert.deepEqual(catalogs,before);
  }finally{setWardrobeCatalogs({male,female});}
});
