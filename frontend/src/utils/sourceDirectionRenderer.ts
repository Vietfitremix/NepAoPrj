import { getWardrobe, selectedAccessories } from './maleWardrobe.ts';
import type { MaleSelection, WardrobeCharacter, WardrobeItem } from './maleWardrobe.ts';
import { characterBaseFile, directionalGarmentFile, leftGarmentSourceFile } from './characterViews.ts';
import type { CharacterView } from './characterViews.ts';
import {styledGarment,patternFile} from './wardrobeStyles.ts';
import type {GarmentStyle} from './wardrobeStyles.ts';
import { fitGarment } from './garmentFit.ts';
import {fitFootwear} from './footwearFit.ts';
import {fitAccessory} from './accessoryFit.ts';

export type CharacterImages = Record<string, HTMLImageElement | HTMLCanvasElement>;
const handFile = (view: CharacterView) => `views/hands-${view}.png`;
const bottomBaseFile = (view: CharacterView) => `views/base-bottom-${view}.png`;
const shoeBaseFile = (view: CharacterView,bottom:boolean) => `views/base-${bottom?'bottom-':''}shoes-${view}.png`;
type Polygon = number[][];
export const handRegions: Record<WardrobeCharacter, Record<CharacterView, Polygon[]>> = {
  male: {
    front: [[[200,710],[268,710],[283,782],[267,856],[236,866],[210,828],[195,770]],[[756,710],[824,710],[829,770],[814,828],[788,866],[757,856],[741,782]]],
    right: [[[493,710],[543,708],[570,753],[584,799],[577,837],[558,862],[535,858],[514,840],[502,811],[489,764]]],
    left: [[[452,715],[499,723],[515,765],[507,810],[486,868],[465,875],[444,852],[433,802],[436,758]]],
    back: [[[215,715],[260,728],[295,795],[280,850],[254,871],[232,850],[208,811]]],
  },
  female: {
    front: [[[255,711],[319,711],[331,769],[315,836],[293,863],[267,847],[246,800]],[[705,711],[769,711],[778,800],[757,847],[731,863],[709,836],[693,769]]],
    right: [[[502,727],[551,727],[568,764],[574,806],[565,837],[549,857],[534,854],[526,841],[511,824],[501,799],[498,759]]],
    left: [[[452,728],[497,735],[513,766],[504,812],[487,863],[468,878],[447,856],[440,814],[442,769]]],
    back: [[[256,710],[294,727],[309,772],[297,832],[283,863],[264,850],[249,820],[245,769]]],
  },
};

// Extract only visible hand skin from the original avatar, preserving identity.
// Gray base shorts and the source background must never cover a selected item.
export function withHandForeground(images: Record<string, HTMLImageElement>, character: WardrobeCharacter): CharacterImages {
  const result: CharacterImages = { ...images };
  for (const view of ['front', 'right', 'left', 'back'] as const) {
    const base = images[characterBaseFile(character, view)];
    if (!base) continue;
    // Neutral source shorts have a loose silhouette. Remove their gray fabric
    // beneath a chosen bottom so slim pants and skirts can define their own cut.
    const bottomBase = document.createElement('canvas');
    bottomBase.width = 1024; bottomBase.height = 1536;
    const bottomContext = bottomBase.getContext('2d');
    if (bottomContext) {
      bottomContext.drawImage(base, 0, 0, 1024, 1536);
      const end = character === 'male' ? 955 : 855;
      const region = bottomContext.getImageData(300, 650, 424, end - 650);
      for (let i = 0; i < region.data.length; i += 4) {
        const r = region.data[i], g = region.data[i+1], b = region.data[i+2];
        if (Math.abs(r-g) < 18 && Math.abs(g-b) < 18 && r < g*1.065) region.data[i+3] = 0;
      }
      bottomContext.putImageData(region, 300, 650);
      result[bottomBaseFile(view)] = bottomBase;
    }
    // Closed footwear replaces the neutral avatar's exposed toes and soles.
    for(const bottom of [false,true]){
      const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=1536;
      const context=canvas.getContext('2d');if(!context)continue;
      context.drawImage(bottom?(result[bottomBaseFile(view)]??base):base,0,0,1024,1536);
      context.clearRect(290,1360,460,176);result[shoeBaseFile(view,bottom)]=canvas;
    }
    const canvas = document.createElement('canvas');
    canvas.width = 1024; canvas.height = 1536;
    const context = canvas.getContext('2d');
    if (!context) continue;
    const regions = [...handRegions[character][view]];
    if (view === 'back') regions.push(regions[0].map(([x,y]) => [1024-x,y]));
    context.beginPath();
    for (const region of regions) {
      region.forEach(([x,y], index) => index === 0 ? context.moveTo(x,y) : context.lineTo(x,y));
      context.closePath();
    }
    context.clip();
    context.drawImage(base, 0, 0, 1024, 1536);
    const pixels = context.getImageData(0, 0, 1024, 1536);
    const data = pixels.data;
    for (let i = 0; i < data.length; i += 4) {
      const a = data[i+3];
      if (!a) continue;
      const r = data[i], g = data[i+1], b = data[i+2];
      if (a < 220 || r < g * 1.06 || g < b * 1.06) data[i+3] = 0;
    }
    context.putImageData(pixels, 0, 0);
    result[handFile(view)] = canvas;
  }
  return result;
}

export function renderSourceDirection(context: CanvasRenderingContext2D, images: CharacterImages,
  selection: MaleSelection, character: WardrobeCharacter, view: CharacterView) {
  const catalog = getWardrobe(character);
  const shirt = catalog.outfits.find(item => item.id === selection.shirt);
  const pants = catalog.pants.find(item => item.id === selection.pants);
  const shoes = catalog.shoes.find(item => item.id === selection.shoes);
  const accessories = selectedAccessories(selection, character);
  const draw = (file: string,style?:GarmentStyle,offsetY=0,offsetX=0) => {
    const rawLeft=shirt && view==='left' && file===directionalGarmentFile(shirt.file,view)
      ? images[leftGarmentSourceFile(shirt.reference)] : undefined;
    const image = rawLeft || images[file];
    const pattern=patternFile(style);
    if (image) {
      const styled=styledGarment(image,style,pattern?images[pattern]:undefined);
      const fitted=shirt && file===directionalGarmentFile(shirt.file,view)
        ? fitGarment(styled,images[characterBaseFile(character,view)],character,shirt.id,view,!!rawLeft) : styled;
      context.drawImage(fitted, offsetX, offsetY, 1024, 1536);
    }
  };
  const shirtFile = shirt ? directionalGarmentFile(shirt.file, view) : undefined;
  const accessoryBody = images[characterBaseFile(character,view)];
  const fittedAccessories = new Map<string, ReturnType<typeof fitAccessory>>();
  // Fit carriers first so charms attach to the bag currently being worn.
  for (const item of [...accessories].sort((a,b)=>Number(a.slot==='bagCharm')-Number(b.slot==='bagCharm'))) {
    const image = images[directionalGarmentFile(item.file,view)];
    if (!image) continue;
    const carrier = accessories.find(other=>other.slot==='bag') ?? accessories.find(other=>other.slot==='backpack');
    const carrierTarget = carrier ? fittedAccessories.get(carrier.id)?.target : undefined;
    fittedAccessories.set(item.id,fitAccessory(image,accessoryBody,item,character,view,
      item.slot==='bagCharm' && carrier && carrierTarget ? {target:carrierTarget,id:carrier.id,slot:carrier.slot} : undefined));
  }
  const drawAccessory=(item:WardrobeItem)=>{
    const fitted = fittedAccessories.get(item.id); if (!fitted) return;
    context.save();context.shadowColor='rgba(28,23,18,.18)';context.shadowBlur=item.slot==='headwear'?3:1.4;
    context.shadowOffsetY=item.slot==='headwear'?1.5:1;
    context.drawImage(fitted.image,fitted.offsetX,fitted.offsetY,fitted.image.width || 1024,fitted.image.height || 1536);context.restore();
  };
  const split = view === 'right' ? (character === 'male' ? 506 : 509) : (character === 'male' ? 520 : 505);
  // Open the left slit gradually below the hip instead of cutting a rectangular
  // patch of trousers through the torso at wrist height.
  const leftSeam = [[split+150,730],[split+135,780],[split+100,835],
    [split+60,890],[split+25,945],[split,1000],[split,1536]];
  const splitPanels = shirt && shirt.id !== 'ba-ba' && (view === 'left' || view === 'right');
  context.save();
  const rearAccessories=accessories.filter(item=>item.rearViews?.includes(view)
    && (item.slot==='backpack'||item.slot==='glasses'||item.id==='tui-deo-cheo'));
  const charm=accessories.find(item=>item.slot==='bagCharm');
  const charmCarrier=accessories.find(item=>item.slot==='bag') ?? accessories.find(item=>item.slot==='backpack');
  const rearCharm=charm && charmCarrier && rearAccessories.includes(charmCarrier);
  for (const fitted of fittedAccessories.values()) if (fitted.rearImage)
    context.drawImage(fitted.rearImage, fitted.offsetX, fitted.offsetY);
  for(const item of rearAccessories)drawAccessory(item);
  if(rearCharm)drawAccessory(charm);
  const bodyFile=pants&&images[bottomBaseFile(view)]?bottomBaseFile(view):characterBaseFile(character,view);
  const shoeImage=shoes?images[directionalGarmentFile(shoes.file,view)]:undefined;
  const shoeStyle=selection.styles?.shoes,shoePattern=patternFile(shoeStyle);
  const styledShoe=shoeImage?styledGarment(shoeImage,shoeStyle,shoePattern?images[shoePattern]:undefined):undefined;
  const footwear=shoes&&styledShoe&&images[bodyFile]?.width?
    fitFootwear(styledShoe,images[bodyFile],character,shoes.id,view):undefined;
  if(footwear)context.drawImage(footwear.body,0,0,1024,1536);
  else {
    const preparedShoes=shoes?.coversFeet?shoeBaseFile(view,!!pants):undefined;
    draw(preparedShoes&&images[preparedShoes]?preparedShoes:bodyFile);
  }
  if (splitPanels && shirtFile) {
    context.save(); context.beginPath();
    const rear = view === 'right'
      ? [[0,740],[split-40,740],[split,840],[split,1536],[0,1536]]
      : [leftSeam[0],[1024,730],[1024,1536],...leftSeam.slice(1).reverse()];
    rear.forEach(([x,y], index) => index === 0 ? context.moveTo(x,y) : context.lineTo(x,y));
    context.closePath();
    context.clip(); draw(shirtFile,selection.styles?.shirt); context.restore();
  }
  if(footwear){
    context.drawImage(footwear.shoe,0,0,1024,1536);
  }else if (shoes) draw(directionalGarmentFile(shoes.file, view),selection.styles?.shoes);
  if (pants) draw(directionalGarmentFile(pants.file, view),selection.styles?.pants);
  if (shirtFile) {
    context.save();
    if (splitPanels) {
      const polygon = view === 'right'
        ? [[0,0],[1024,0],[1024,1536],[split,1536],[split,840],[split-40,740],[0,740]]
        : [[0,0],[1024,0],[1024,730],...leftSeam,[0,1536]];
      context.beginPath();
      polygon.forEach(([x,y], index) => index === 0 ? context.moveTo(x,y) : context.lineTo(x,y));
      context.closePath(); context.clip();
    }
    draw(shirtFile,selection.styles?.shirt); context.restore();
  }
  // Bags and fans sit underneath the original hand skin, preserving the grip.
  for (const item of accessories.filter(item=>(item.slot==='bag'||item.slot==='fan')&&!rearAccessories.includes(item))) drawAccessory(item);
  if (shirt || pants || accessories.some(item=>item.slot==='bag'||item.slot==='fan')) draw(handFile(view));
  // Side-view backpack pouches sit behind the body, with near straps over clothes.
  for(const item of rearAccessories.filter(item=>item.slot==='backpack'||item.id==='tui-deo-cheo')){
    context.save();context.beginPath();context.rect(view==='left'?350:510,250,190,530);context.clip();
    drawAccessory(item);context.restore();
  }
  if(charm&&!rearCharm)drawAccessory(charm);
  // Jewellery follows the body; flowers precede headwear so caps can cover them.
  for (const slot of ['backpack','hipChain','gloves','necklace','earrings','bracelet','headphones','glasses','hairAccessory','headwear'])
    for (const item of accessories.filter(item=>item.slot===slot&&!rearAccessories.includes(item))) drawAccessory(item);
  context.restore();
}
