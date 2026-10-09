import type { WardrobeCharacter } from './maleWardrobe.ts';
import type { CharacterView } from './characterViews.ts';

type Raster = HTMLImageElement | HTMLCanvasElement;
type Point = [number, number];
const width = 1024, height = 1536;
const openings: Record<WardrobeCharacter, Record<string, Point[]>> = {
  male: {
    'ngu-than': [[455,238],[478,236],[544,236],[566,239],[554,264],[536,275],[513,286],[497,281],[475,268]],
    'nhat-binh': [[466,243],[488,241],[541,241],[558,244],[546,267],[525,275],[513,279],[500,274],[478,265]],
    'tu-than': [[464,241],[487,239],[541,239],[555,242],[545,269],[527,279],[512,286],[497,278],[478,266]],
    'ba-ba': [[448,238],[477,238],[545,238],[576,242],[588,274],[578,298],[558,317],[535,328],[512,331],[486,328],[465,319],[447,300],[433,274]],
  },
  female: {
    jade: [[454,247],[477,245],[548,245],[569,249],[551,277],[532,284],[513,291],[503,287],[484,279],[466,275]],
    rose: [[454,247],[477,245],[548,245],[569,249],[551,277],[532,284],[513,291],[503,287],[484,279],[466,275]],
    'ngu-than': [[452,238],[476,236],[548,236],[570,239],[557,268],[535,279],[513,289],[493,278],[471,267]],
    'nhat-binh': [[459,245],[481,243],[546,243],[565,246],[548,289],[530,295],[515,303],[510,303],[492,294],[475,285]],
    'tu-than': [[461,251],[483,249],[545,249],[564,252],[549,285],[530,295],[515,303],[508,300],[492,289],[475,280]],
    'ba-ba': [[460,252],[486,248],[538,248],[564,252],[577,285],[590,302],[581,320],[561,338],[537,346],[512,349],[489,346],[466,338],[447,320],[437,302],[449,285]],
  },
};

const clamp = (n: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, n));
const smooth = (lo: number, hi: number, n: number) => {
  const t = clamp((n-lo)/(hi-lo), 0, 1);
  return t*t*(3-2*t);
};
const skin = (pixels: Uint8ClampedArray, index: number) => pixels[index+3]>220
  && pixels[index]>pixels[index+1]*1.08 && pixels[index+1]>pixels[index+2]*1.08;
function canvas() {
  const result = document.createElement('canvas'); result.width = width; result.height = height;
  return result;
}
function path(context: CanvasRenderingContext2D, polygon: Point[]) {
  const last=polygon.at(-1)!,first=polygon[0];
  context.beginPath();context.moveTo((last[0]+first[0])/2,(last[1]+first[1])/2);
  polygon.forEach(([x,y],i)=>{
    const next=polygon[(i+1)%polygon.length];
    context.quadraticCurveTo(x,y,(x+next[0])/2,(y+next[1])/2);
  });
  context.closePath();
}
function rowSpan(pixels: Uint8ClampedArray, y: number, mainBody=false): Point | undefined {
  // Ignore isolated matte specks rather than stretching the garment to them.
  let start=-1,best:Point|undefined,lo=width,hi=-1;
  for(let x=0;x<=width;x++){
    if(x<width&&pixels[(y*width+x)*4+3]>230){if(start<0)start=x;}
    else if(start>=0){
      if(x-start>=4){
        lo=Math.min(lo,start);hi=Math.max(hi,x);
        if(!best||x-start>best[1]-best[0])best=[start,x];
      }
      start=-1;
    }
  }
  return mainBody?best:hi>=lo?[lo,hi]:undefined;
}

// Interpolate the source rows with a continuous slope. Independent rectangular
// bands introduce visible cuts at the collar, shoulder and upper arm.
export function sourceRow(y: number, stops: Point[]): number {
  if(y<=stops[0][0])return stops[0][1];
  if(y>=stops.at(-1)![0])return stops.at(-1)![1];
  const index=stops.findIndex(stop=>stop[0]>=y),a=stops[index-1],b=stops[index];
  const slopes=stops.slice(1).map((stop,i)=>(stop[1]-stops[i][1])/(stop[0]-stops[i][0]));
  const tangent=(i:number)=>{
    if(i===0)return slopes[0];
    if(i===stops.length-1)return slopes.at(-1)!;
    const a=slopes[i-1],b=slopes[i];
    return a*b<=0?0:2*a*b/(a+b);
  };
  const t=(y-a[0])/(b[0]-a[0]),d=b[0]-a[0];
  return (2*t**3-3*t*t+1)*a[1]+(t**3-2*t*t+t)*d*tangent(index-1)
    +(-2*t**3+3*t*t)*b[1]+(t**3-t*t)*d*tangent(index);
}

function fitLeft(source: HTMLCanvasElement, basePixels: Uint8ClampedArray,
  character: WardrobeCharacter, id: string): HTMLCanvasElement {
  const sourceContext=source.getContext('2d')!;
  const pixels=sourceContext.getImageData(0,0,width,height);
  for(let i=3;i<pixels.data.length;i+=4)pixels.data[i]=clamp((pixels.data[i]-220)/35,0,1)*255;
  sourceContext.putImageData(pixels,0,0);
  const spans=Array.from({length:height},(_,y)=>rowSpan(pixels.data,y));
  const first=spans.findIndex(Boolean),last=height-1-[...spans].reverse().findIndex(Boolean);
  if(first<0||last<=first)return source;
  const short=id==='ba-ba',length=last-first+1;
  const top=short?(character==='male'?250:262):(character==='male'?224:244);
  const hem=short?750:character==='male'?(id==='nhat-binh'?1190:1140):1230;
  const cuff=short ? .9 : character==='female' ? .43 : id==='navy' ? .59 : .56;
  const stops:Point[]=short?[[top,first],[302,first+length*.1],[hem,last]]
    :[[top,first],[302,first+length*.1],[735,first+length*cuff],[hem,last]];
  const region=(rows:(Point|undefined)[],from:number,to:number):Point=>{
    const present=rows.slice(Math.round(from),Math.round(to)).filter((row):row is Point=>!!row);
    return [Math.min(...present.map(row=>row[0])),Math.max(...present.map(row=>row[1]))];
  };
  const bodySpans=Array.from({length:height},(_,y)=>rowSpan(basePixels,y,true));
  const body=region(bodySpans,300,725),shape=region(spans,first+length*.12,first+length*.5);
  const scale=(body[1]-body[0]+(id==='nhat-binh'?55:24))/(shape[1]-shape[0]);
  const offset=(body[0]+body[1])/2-(shape[0]+shape[1])/2*scale;
  const result=canvas(),context=result.getContext('2d')!;
  context.imageSmoothingEnabled=true;context.imageSmoothingQuality='high';
  const average=(rows:(Point|undefined)[],y:number):Point|undefined=>{
    const present=rows.slice(Math.max(0,Math.round(y)-12),Math.min(height,Math.round(y)+13))
      .filter((row):row is Point=>!!row);
    return present.length?[present.reduce((s,r)=>s+r[0],0)/present.length,present.reduce((s,r)=>s+r[1],0)/present.length]:undefined;
  };
  for(let y=top;y<hem;y++){
    const sy=sourceRow(y,stops),span=average(spans,sy),target=average(bodySpans,y);
    if(!span)continue;
    const fullness=id==='nhat-binh'?.88-.23*smooth(400,480,y):.88;
    const weight=smooth(270,365,y)*(1-smooth(705,805,y))*fullness;
    const lo=span[0]*scale+offset,hi=span[1]*scale+offset;
    const x=target?lo*(1-weight)+(target[0]-7)*weight:lo;
    const right=target?hi*(1-weight)+(target[1]+7)*weight:hi;
    const next=sourceRow(y+1,stops);
    // Full-width source strips keep the antialiased source outline; cropping
    // each strip to an averaged span would recreate stair steps at the edges.
    const sx=(right-x)/(span[1]-span[0]);
    context.drawImage(source,0,sy,width,Math.max(.1,next-sy),x-span[0]*sx,y,width*sx,1.05);
  }
  return result;
}

function fitShoulders(source: HTMLCanvasElement, bodyPixels: Uint8ClampedArray, character: WardrobeCharacter, view: CharacterView): HTMLCanvasElement {
  const pixels=source.getContext('2d')!.getImageData(0,0,width,420).data;
  const shifts=Array.from({length:width},(_,x)=>{
    let top=420,neutral=420,bodyTop=420;
    for(let y=235;y<350;y++){
      const i=(y*width+x)*4;
      if(top===420&&pixels[i+3]>230)top=y;
      if(bodyTop===420&&bodyPixels[i+3]>230)bodyTop=y;
      const r=bodyPixels[i],g=bodyPixels[i+1],b=bodyPixels[i+2];
      if(neutral===420&&bodyPixels[i+3]>230&&r>65&&Math.abs(r-g)<18&&Math.abs(g-b)<18)neutral=y;
    }
    if(top>=350)return 0;
    const neutralShift=neutral<top?Math.min(35,top-neutral+4):0;
    if(view!=='front')return neutralShift;
    // Cover exposed shoulder skin while leaving the upright collar in place.
    const edge=Math.min(x,width-x),neckEdge=character==='male'?466:474;
    const shoulderWeight=(1-smooth(neckEdge-8,neckEdge+2,edge))*smooth(315,370,edge);
    const shoulderShift=bodyTop<top?Math.min(35,top-bodyTop+2)*shoulderWeight:0;
    return Math.max(neutralShift,shoulderShift);
  });
  if(!shifts.some(Boolean))return source;
  const result=canvas(),context=result.getContext('2d')!;
  for(let x=0;x<width;x++){
    const neighbors=shifts.slice(Math.max(0,x-5),Math.min(width,x+6));
    const shift=neighbors.reduce((sum,n)=>sum+n,0)/neighbors.length;
    // Stretch a continuous section of the original texture instead of filling
    // gaps with repeated edge pixels, which creates blocky shoulder tabs.
    context.drawImage(source,x,220,1,200,x,220-shift,1,200+shift);
    context.drawImage(source,x,420,1,height-420,x,420,1,height-420);
  }
  return result;
}

const cache=new WeakMap<Raster,WeakMap<Raster,Map<string,HTMLCanvasElement>>>();
export function fitGarment(image: Raster, base: Raster | undefined, character: WardrobeCharacter,
  id: string, view: CharacterView, rawLeft=false): Raster {
  // Pure draw-order tests and unsupported environments retain the source layer.
  if(typeof document==='undefined'||!base||!image.width||!base.width)return image;
  let byBase=cache.get(image);if(!byBase){byBase=new WeakMap();cache.set(image,byBase);}
  let variants=byBase.get(base);if(!variants){variants=new Map();byBase.set(base,variants);}
  const key=character+'/'+id+'/'+view+'/'+rawLeft;
  const cached=variants.get(key);if(cached)return cached;
  const body=canvas(),bc=body.getContext('2d')!;bc.drawImage(base,0,0,width,height);
  const bodyPixels=bc.getImageData(0,0,width,height).data;
  let result=canvas();result.getContext('2d')!.drawImage(image,0,0,width,height);
  if(view==='left'&&rawLeft)result=fitLeft(result,bodyPixels,character,id);
  result=fitShoulders(result,bodyPixels,character,view);
  const context=result.getContext('2d')!;

  const opening=view==='front'?openings[character][id]:undefined;
  if(opening){
    // Put the original avatar's neck inside the collar, ahead of its back rim
    // and behind its front rim. Fill only source undershirt pixels from nearby
    // original neck skin, so recolouring fabric never recolours the person.
    const neck=canvas(),nc=neck.getContext('2d')!;nc.drawImage(body,0,0);
    const sample=nc.getImageData(400,240,220,125);
    const originalNeck=new Uint8ClampedArray(sample.data);
    for(let y=0;y<125;y++)for(let x=0;x<220;x++){
      const i=(y*220+x)*4;
      if(originalNeck[i+3]<230)continue;
      if(skin(originalNeck,i))continue;
      let found=false;
      for(let sy=y-1;sy>=0;sy--){
        const p=(sy*220+x)*4;if(!skin(originalNeck,p))continue;
        const shade=1-Math.min(.12,(y-sy)*.0015);
        for(let c=0;c<3;c++)sample.data[i+c]=originalNeck[p+c]*shade;
        sample.data[i+3]=255;found=true;break;
      }
      if(!found && y>25){
        // The wider round neck can reveal chest hidden by the base tank top.
        // Sample the avatar's own adjacent skin rather than retaining gray fabric.
        const sx=clamp(x,65,155),p=(Math.min(y,25)*220+sx)*4;
        if(skin(originalNeck,p)){for(let c=0;c<3;c++)sample.data[i+c]=originalNeck[p+c]*.96;sample.data[i+3]=255;}
      }
    }
    nc.putImageData(sample,400,240);
    context.save();path(context,opening);context.clip();context.drawImage(neck,0,0);
    // A narrow contact shadow makes the fabric rim sit against the skin.
    context.strokeStyle='rgba(62,35,21,.12)';context.lineWidth=2;
    context.beginPath();opening.slice(4).forEach(([x,y],i)=>i?context.lineTo(x,y):context.moveTo(x,y));context.stroke();
    context.restore();
  }
  variants.set(key,result);return result;
}
