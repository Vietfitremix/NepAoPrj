import type {WardrobeCharacter} from './maleWardrobe.ts';
import type {CharacterView} from './characterViews.ts';
type Raster=HTMLImageElement|HTMLCanvasElement;
interface Box {x:number;y:number;width:number;height:number}
const W=1024,H=1536;
function canvas(){const c=document.createElement('canvas');c.width=W;c.height=H;return c;}
function bounds(data:Uint8ClampedArray,x0:number,x1:number,y0:number,y1:number):Box|undefined{
 let l=x1,r=-1,t=y1,b=-1;
 for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++)if(data[(y*W+x)*4+3]>230){
  l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);
 }
 return r>=l?{x:l,y:t,width:r-l+1,height:b-t+1}:undefined;
}
export function closedFootwear(id:string){return !['guoc','dep-le'].includes(id);}
export function footwearDimensions(id:string,profile:boolean,back:boolean){
 const sport=id==='sneakers'||id==='giay-the-thao',flat=id==='flats'||id==='giay-bup-be';
 const sole=id==='guoc'?25:sport||id==='dep-crocs'?12:6;
 const height=profile?(sport?90:flat?62:id==='guoc'?100:id==='dep-crocs'?95:78)
  :back?(sport?88:flat?65:id==='guoc'?85:78)
  :sport?118:flat?102:id==='guoc'?110:108;
 return {height,sole,padding:profile?8:sport?9:6};
}
function polygon(ctx:CanvasRenderingContext2D,box:Box,points:number[][]){
 ctx.beginPath();points.forEach(([u,v],i)=>{
  const x=box.x+u*box.width,y=box.y+v*box.height;
  if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);
 });ctx.closePath();
}
function roundedOpening(ctx:CanvasRenderingContext2D,box:Box,points:number[][]){
 const first=points[0],last=points.at(-1)!;
 ctx.beginPath();ctx.moveTo(box.x+(first[0]+last[0])*box.width/2,box.y+(first[1]+last[1])*box.height/2);
 points.forEach(([x,y],i)=>{const next=points[(i+1)%points.length];
  ctx.quadraticCurveTo(box.x+x*box.width,box.y+y*box.height,
   box.x+(x+next[0])*box.width/2,box.y+(y+next[1])*box.height/2);
 });ctx.closePath();
}
interface FittedFootwear {shoe:Raster;body:Raster}
const cache=new WeakMap<Raster,WeakMap<Raster,Map<string,FittedFootwear>>>();
// Fit existing shoe textures to the measured foot silhouette, independently
// for each leg. Keep the original ankle and use its skin in shoe openings.
export function fitFootwear(image:Raster,body:Raster,character:WardrobeCharacter,id:string,view:CharacterView):FittedFootwear{
 if(typeof document==='undefined'||!image.width||!body.width)return {shoe:image,body};
 let byBody=cache.get(image);if(!byBody){byBody=new WeakMap();cache.set(image,byBody);}
 let variants=byBody.get(body);if(!variants){variants=new Map();byBody.set(body,variants);}
 const key=character+'/'+id+'/'+view,cached=variants.get(key);if(cached)return cached;
 const original=canvas(),oc=original.getContext('2d')!;oc.drawImage(body,0,0,W,H);
 const bodyPixels=oc.getImageData(0,0,W,H).data;
 const source=canvas(),sc=source.getContext('2d')!;sc.drawImage(image,0,0,W,H);
 const sourcePixels=sc.getImageData(0,0,W,H).data;
 const skinMask=canvas(),sm=skinMask.getContext('2d')!,mask=sm.createImageData(W,H);
 for(let i=(1250*W)*4;i<mask.data.length;i+=4)mask.data[i+3]=bodyPixels[i+3]>230?255:0;
 sm.putImageData(mask,0,0);
 const shoe=canvas(),ctx=shoe.getContext('2d')!,fittedBody=canvas(),bc=fittedBody.getContext('2d')!;
 bc.drawImage(original,0,0);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 const profile=view==='left'||view==='right',dimensions=footwearDimensions(id,profile,view==='back');
 const areas=profile?[[280,750]]:[[280,512],[512,750]];
 for(const [x0,x1] of areas){
  const foot=bounds(bodyPixels,x0,x1,1360,1500),crop=bounds(sourcePixels,x0,x1,1250,1500);
  const ankle=bounds(bodyPixels,x0,x1,1300,1305);
  if(!foot||!crop)continue;
  const target={x:foot.x-dimensions.padding,y:foot.y+foot.height+dimensions.sole-dimensions.height,
   width:foot.width+dimensions.padding*2,height:dimensions.height};
  ctx.save();
  // These profile sources contain a second, unworn shoe behind the near one.
  // Retain the near shoe's upper and sole instead of displaying a floating pair.
  const paired=profile&&['giay-bup-be','giay-ta','guoc'].includes(id);
  const nearCrop=paired?{...crop,y:crop.y+crop.height*.28,height:crop.height*.72}:crop;
  if(paired){
   const outline=id==='guoc'?[[0,.45],[.15,.12],[.25,0],[.42,.06],[.52,.28],[1,.24],[1,1],[0,1]]
    :[[0,.46],[.3,.26],[1,0],[1,1],[0,1]];
   polygon(ctx,target,view==='right'?outline.map(([x,y])=>[1-x,y]).reverse():outline);ctx.clip();
  }
  ctx.drawImage(source,nearCrop.x,nearCrop.y,nearCrop.width,nearCrop.height,target.x,target.y,target.width,target.height);
  ctx.restore();
  const pixels=ctx.getImageData(0,0,W,H).data;
  // Clear only the distal foot beneath the fitted upper; the ankle above its
  // rim stays intact. The sole position follows the actual ground in each view.
  const layer=bc.getImageData(0,0,W,H);
  for(let x=Math.max(0,Math.floor(target.x));x<Math.min(W,Math.ceil(target.x+target.width));x++){
   let rim=target.y+target.height*.5;
   if(closedFootwear(id)){
    for(let y=Math.max(0,Math.floor(target.y));y<target.y+target.height;y++){
     if(pixels[(y*W+x)*4+3]>100){rim=y+2;break;}
    }
    // The toe cap replaces the distal foot even where its texture starts
    // below the original instep. Preserve skin only at the heel opening.
    if(profile&&ankle){
     const distance=view==='left'?x-ankle.x:ankle.x+ankle.width-x;
     const t=Math.max(0,Math.min(1,(distance+4)/16)),blend=t*t*(3-2*t);
     rim=1305+(rim-1305)*blend;
    }else if(view==='front')rim=Math.min(rim,1360);
   }else rim=foot.y+foot.height;
   const start=closedFootwear(id)&&profile?1305:1338;
   for(let y=Math.max(start,Math.ceil(rim));y<H;y++)layer.data[(y*W+x)*4+3]=0;
  }
  bc.putImageData(layer,0,0);
  const front=view==='front';
  if(!closedFootwear(id)){
   // Place the avatar's own toes and heel over the insole, behind the strap.
   const openings=profile?[
    [[0,.48],[.18,.48],[.18,.86],[0,.86]],
    [[.68,0],[1,0],[1,.78],[.68,.78]],
   ]:front?[
    [[.16,.70],[.84,.70],[.84,.91],[.16,.91]],
    [[.22,0],[.78,0],[.78,.37],[.22,.37]],
   ]:[[[.2,0],[.8,0],[.8,.45],[.2,.45]]];
   for(const opening of openings){
    ctx.save();polygon(ctx,target,profile&&view==='right'?opening.map(([x,y])=>[1-x,y]).reverse():opening);ctx.clip();
    ctx.globalCompositeOperation='destination-out';ctx.drawImage(skinMask,0,0);
    ctx.globalCompositeOperation='source-over';ctx.drawImage(original,0,0);ctx.restore();
   }
  }else if(front&&['flats','giay-bup-be','hai-theu','giay-ta'].includes(id)){
   ctx.save();roundedOpening(ctx,target,[[.37,.12],[.63,.12],[.73,.29],[.66,.48],[.50,.56],[.34,.48],[.27,.29]]);
   ctx.clip();ctx.globalCompositeOperation='destination-out';ctx.drawImage(skinMask,0,0);
   ctx.globalCompositeOperation='source-over';ctx.drawImage(original,0,0);ctx.restore();
  }
 }
 const result={shoe,body:fittedBody};variants.set(key,result);return result;
}
