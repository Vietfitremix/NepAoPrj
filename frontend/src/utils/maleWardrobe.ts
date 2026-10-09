import male from '../../public/figure/male-layers/catalog.json' with { type: 'json' };
import female from '../../public/figure/female-layers/catalog.json' with { type: 'json' };
import { normalizeGarmentStyles } from './wardrobeStyles.ts';
import type { GarmentStyle, GarmentStyleSlot } from './wardrobeStyles.ts';
export type WardrobeCharacter = 'male' | 'female';
export const accessorySlots = [
 {id:'headwear',name:'Nón / Khăn đội đầu'},
 {id:'headphones',name:'Tai nghe'},
 {id:'glasses',name:'Kính'},
 {id:'hairAccessory',name:'Hoa cài tóc'},
 {id:'necklace',name:'Kiềng cổ'},
 {id:'earrings',name:'Bông tai'},
 {id:'bracelet',name:'Vòng tay'},
 {id:'gloves',name:'Găng tay'},
 {id:'hipChain',name:'Dây xích đeo hông'},
 {id:'backpack',name:'Ba lô'},
 {id:'bag',name:'Túi'},
 {id:'bagCharm',name:'Móc khóa bông'},
 {id:'fan',name:'Quạt'},
] as const;
export type AccessorySlot = typeof accessorySlots[number]['id'];
export interface WardrobeItem {
 id:string; name:string; detail:string; file:string; thumbnail:string; category:string; reference:string;
 gender?:WardrobeCharacter | 'unisex';
 x?:number; y?:number; sx?:number; sy?:number; sourcePrepared?:boolean; offsetY?:number;
 mapY?:number[][]; sleeveX?:number; sleeveDx?:number;
 fitRows?:{y:number;points:number[][]}[]; slot?:AccessorySlot; rearViews?:string[]; coversFeet?:boolean; footbedClipY?:number;
}
export interface WardrobeCatalog {
 width:number; height:number; base:string; outfits:WardrobeItem[]; pants:WardrobeItem[];
 shoes:(WardrobeItem & {crops:number[][]})[]; accessories:WardrobeItem[];
}
function genderWardrobe(catalog:WardrobeCatalog,character:WardrobeCharacter):WardrobeCatalog {
 const allowed=(item:WardrobeItem)=>!item.gender || item.gender==='unisex' || item.gender===character;
 return {...catalog,outfits:catalog.outfits.filter(allowed),pants:catalog.pants.filter(allowed),
  shoes:catalog.shoes.filter(allowed),accessories:catalog.accessories.filter(allowed)};
}
const wardrobes:Record<WardrobeCharacter,WardrobeCatalog> = {
 male:genderWardrobe(male as WardrobeCatalog,'male'),
 female:genderWardrobe(female as WardrobeCatalog,'female'),
};
export let maleWardrobe = wardrobes.male;
export function setWardrobeCatalogs(value:Record<WardrobeCharacter,WardrobeCatalog>) {
 for(const character of ['male','female'] as const) {
  const catalog=value[character];
  if(!catalog || !catalog.base || !catalog.width || !catalog.height ||
    !['outfits','pants','shoes','accessories'].every(key=>Array.isArray(catalog[key as keyof WardrobeCatalog])))
   throw new Error('Dữ liệu tủ đồ trên máy chủ chưa đầy đủ.');
 }
 wardrobes.male=genderWardrobe(value.male,'male');wardrobes.female=genderWardrobe(value.female,'female');maleWardrobe=wardrobes.male;
}
export const maleAssetRoot = '/figure/male-layers/';
export const maleSelectionKey = 'viet-fit-male-outfit';
export const characterSelectionKey = 'viet-fit-character';
export const characters = [{id:'male',name:'Nam'},{id:'female',name:'Nữ'}] as const;
export const assetRoot = (character: WardrobeCharacter) => '/figure/'+character+'-layers/';
export const selectionKey = (character: WardrobeCharacter) => 'viet-fit-'+character+'-outfit';
export const getWardrobe = (character: WardrobeCharacter) => wardrobes[character];
export function normalizeCharacter(value: unknown): WardrobeCharacter { return value === 'female' ? 'female' : 'male'; }
export interface MaleSelection { shirt: string | null; pants: string | null; shoes?: string | null; accessories?:Partial<Record<AccessorySlot,string|null>>; styles?:Partial<Record<GarmentStyleSlot,GarmentStyle>> }
export function selectedAccessories(selection:MaleSelection,character:WardrobeCharacter) {
 return getWardrobe(character).accessories.filter(item=>item.slot && selection.accessories?.[item.slot]===item.id);
}
export function selectedWardrobeItems(selection:MaleSelection,character:WardrobeCharacter) {
 const catalog=getWardrobe(character);
 return [catalog.outfits.find(item=>item.id===selection.shirt),catalog.pants.find(item=>item.id===selection.pants),
  catalog.shoes.find(item=>item.id===selection.shoes),...selectedAccessories(selection,character)].filter((item):item is WardrobeItem=>!!item);
}
export function normalizeMaleSelection(value: unknown, character: WardrobeCharacter = 'male'): MaleSelection {
 const catalog=getWardrobe(character);
 if(value==='base')return {shirt:null,pants:null,shoes:null};
 if(typeof value==='string' && catalog.outfits.some(x=>x.id===value))value={shirt:value,pants:catalog.pants[0].id};
 const saved=value && typeof value==='object' && !Array.isArray(value)?value as MaleSelection:undefined;
 const normalized:MaleSelection = {shirt:saved?.shirt===null?null:catalog.outfits.find(x=>x.id===saved?.shirt)?.id??catalog.outfits[0].id,
 pants:saved?.pants===null?null:catalog.pants.find(x=>x.id===saved?.pants)?.id??catalog.pants[0].id,
 shoes:catalog.shoes.find(x=>x.id===saved?.shoes)?.id??null};
 if(saved?.accessories && typeof saved.accessories==='object' && !Array.isArray(saved.accessories)) {
  normalized.accessories={};
  for(const {id:slot} of accessorySlots) {
   const id=saved.accessories[slot];
   normalized.accessories[slot]=catalog.accessories.find(item=>item.slot===slot && item.id===id)?.id??null;
  }
 }
 if(saved?.styles) normalized.styles=normalizeGarmentStyles(saved.styles);
 return normalized;
}
export function readMaleSelection(raw:string|null,character:WardrobeCharacter='male') {
 try{return normalizeMaleSelection(raw===null?null:JSON.parse(raw),character);}catch{return normalizeMaleSelection(raw,character);}
}
export function maleLayers(selection:MaleSelection,character:WardrobeCharacter='male'){
 const catalog=getWardrobe(character), normalized=normalizeMaleSelection(selection,character);
 const shirt=catalog.outfits.find(x=>x.id===normalized.shirt),pants=catalog.pants.find(x=>x.id===normalized.pants);
 return [{file:catalog.base,x:0,y:0,width:1024,height:1536},
 ...[pants,shirt].filter(x=>!!x).map(item=>({...item!,x:(1024-1024*(item!.sx??1))/2+(item!.x??0),y:item!.y??0,width:1024*(item!.sx??1),height:1536*(item!.sy??1)}))];
}
