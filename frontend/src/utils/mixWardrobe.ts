import type { Changes, MixConfig, Outfit } from '../types';
import { getWardrobe, normalizeMaleSelection } from './maleWardrobe.ts';
import type { MaleSelection, WardrobeCharacter } from './maleWardrobe.ts';
import { apiAccessoryItems, apiColorHex, apiFootwearItems, outfitPreview } from './outfitPreview.ts';

const garmentCodes:Record<string,string>={navy:'AO_DAI',burgundy:'AO_DAI',teal:'AO_DAI',jade:'AO_DAI',rose:'AO_DAI',
  'tu-than':'AO_TU_THAN','ngu-than':'AO_NGU_THAN','nhat-binh':'NHAT_BINH','ba-ba':'AO_BA_BA'};
const accessoryCodes:Record<string,string>={
  'non-la':'NON_LA','non-quai-thao':'NON_QUAI_THAO','khan-van':'KHAN_VAN','khan-mo-qua':'KHAN_MO_QUA',
  'khan-xep':'KHAN_XEP','hoa-cai-toc':'HOA_CAI_TOC','tui-coi':'MINIMAL_BAG','quat-giay':'FAN',
  'kieng-bac':'KIENG_BAC','bong-tai':'TRANG_SUC','vong-tay':'TRANG_SUC',
  sneakers:'WHITE_SNEAKERS',guoc:'GUOC','hai-theu':'HAI_THEU','giay-bup-be':'GIAY_BUP_BE',flats:'GIAY_BUP_BE','giay-ta':'GIAY_TA',
  ivory:'QUAN_LUA','skirt-long-ivory':'VAY_DUP','skirt-short-navy':'VAY_XEP_LY',
};
const originalShirtColors:Record<string,string>={navy:'#23415b',burgundy:'#8b2635',teal:'#397c78',jade:'#39705b',rose:'#de91aa',
  'tu-than':'#876044','ngu-than':'#b52838','nhat-binh':'#e2b44b','ba-ba':'#fff4db'};

function nearestColor(hex:string|undefined,colors:Outfit['colors']) {
  if(!hex || !/^#[a-f0-9]{6}$/i.test(hex))return undefined;
  const rgb=(value:string)=>[1,3,5].map(i=>parseInt(value.slice(i,i+2),16));
  const target=rgb(hex);
  return colors.filter(item=>item.hex && /^#[a-f0-9]{6}$/i.test(item.hex))
    .map(item=>({code:item.code,distance:rgb(item.hex!).reduce((sum,v,i)=>sum+(v-target[i])**2,0)}))
    .sort((a,b)=>a.distance-b.distance)[0]?.code;
}

/** Keep every raster choice while projecting supported codes for the existing API. */
export function configureWardrobe(config: MixConfig, raw: MaleSelection, character: WardrobeCharacter, outfits: Outfit[]): MixConfig {
  const selection=normalizeMaleSelection(raw,character);
  const outfitCode=garmentCodes[selection.shirt || ''] || config.outfitCode;
  const outfit=outfits.find(item=>item.code===outfitCode);
  const supported=new Set(outfit?.accessories.map(item=>item.code));
  const ids=[selection.pants,selection.shoes,...Object.values(selection.accessories || {})];
  const codes=[...new Set(ids.map(id=>accessoryCodes[id || '']).filter(code=>code && supported.has(code)))];
  const mainColor=selection.styles?.shirt?.color || originalShirtColors[selection.shirt || ''];
  const colorCode=nearestColor(mainColor,outfit?.colors || [])
    || (outfit?.colors.some(item=>item.code===config.colorCode)?config.colorCode:outfit?.colors[0]?.code) || config.colorCode;
  return {...config,outfitCode,colorCode,accessoryCodes:codes,wardrobe:{character,selection}};
}

export function initialWardrobe(config: MixConfig, character: WardrobeCharacter) {
  return {character,selection:normalizeMaleSelection(outfitPreview(config,character),character)};
}

/** Apply AI changes to the visible wardrobe without discarding unrelated modern pieces. */
export function remixWardrobe(config: MixConfig, changes: Changes): MixConfig['wardrobe'] {
  if (!config.wardrobe) return undefined;
  const {character}=config.wardrobe;
  const selection=normalizeMaleSelection(config.wardrobe.selection,character);
  const wardrobe=getWardrobe(character);
  selection.accessories={...selection.accessories};
  selection.styles={...selection.styles};
  if (changes.colorCode && apiColorHex[changes.colorCode]) {
    selection.styles.shirt={...selection.styles.shirt,color:apiColorHex[changes.colorCode]};
  }
  for (const code of changes.removeAccessories || []) {
    if (selection.shoes===apiFootwearItems[code]) selection.shoes=null;
    if (code==='QUAN_LUA' && selection.pants==='ivory' || code==='VAY_DUP' && selection.pants==='skirt-long-ivory'
      || code==='VAY_XEP_LY' && selection.pants==='skirt-short-navy') selection.pants=null;
    for (const item of wardrobe.accessories) {
      if (item.slot && apiAccessoryItems[code]?.includes(item.id) && selection.accessories[item.slot]===item.id)
        selection.accessories[item.slot]=null;
    }
  }
  for (const code of changes.addAccessories || []) {
    const shoe=apiFootwearItems[code];
    if (wardrobe.shoes.some(item=>item.id===shoe)) selection.shoes=shoe;
    const bottom=code==='QUAN_LUA'?'ivory':code==='VAY_DUP'?'skirt-long-ivory':code==='VAY_XEP_LY'?'skirt-short-navy':null;
    if (bottom && wardrobe.pants.some(item=>item.id===bottom)) selection.pants=bottom;
    for (const item of wardrobe.accessories) {
      if (item.slot && apiAccessoryItems[code]?.includes(item.id)) selection.accessories[item.slot]=item.id;
    }
  }
  return {character,selection};
}
