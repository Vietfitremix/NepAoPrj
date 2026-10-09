import patternCatalog from '../../public/figure/patterns/catalog.json' with {type:'json'};
export const garmentStyleSlots = ['shirt','pants','shoes'] as const;
export type GarmentStyleSlot = typeof garmentStyleSlots[number];
export interface GarmentStyle {color?:string|null;pattern?:string|null}
export let wardrobePatterns=patternCatalog;
export let wardrobeColors=[
 {name:'Đỏ',value:'#b52838'},{name:'Hồng',value:'#de91aa'},{name:'Vàng',value:'#e2b44b'},
 {name:'Xanh lá',value:'#39705b'},{name:'Xanh dương',value:'#32679e'},{name:'Tím',value:'#765a94'},
 {name:'Nâu',value:'#876044'},{name:'Trắng',value:'#eee9dc'},{name:'Đen',value:'#24242a'},
];
export function setWardrobeStyles(patterns:typeof patternCatalog,colors:typeof wardrobeColors) {
 if(!Array.isArray(patterns) || !Array.isArray(colors) || !colors.length)
  throw new Error('Dữ liệu màu và họa tiết trên máy chủ chưa đầy đủ.');
 wardrobePatterns=patterns;wardrobeColors=colors;
}
export function normalizeGarmentStyles(value:unknown):Partial<Record<GarmentStyleSlot,GarmentStyle>> {
 const result:Partial<Record<GarmentStyleSlot,GarmentStyle>>={};
 if(!value||typeof value!=='object'||Array.isArray(value))return result;
 for(const slot of garmentStyleSlots){
  const raw=(value as Record<string,unknown>)[slot];
  if(!raw||typeof raw!=='object'||Array.isArray(raw))continue;
  const style=raw as GarmentStyle;
  result[slot]={color:typeof style.color==='string'&&/^#[a-f0-9]{6}$/i.test(style.color)?style.color.toLowerCase():null,
   pattern:wardrobePatterns.some(item=>item.id===style.pattern)?style.pattern:null};
 }
 return result;
}
export function patternFile(style?:GarmentStyle):string|undefined {
 return wardrobePatterns.find(item=>item.id===style?.pattern)?.file;
}
export function colorizePixels(data:Uint8ClampedArray,color:string) {
 if(!/^#[a-f0-9]{6}$/i.test(color))return;
 const target=[1,3,5].map(start=>parseInt(color.slice(start,start+2),16));
 let total=0,weight=0;
 for(let i=0;i<data.length;i+=4){const a=data[i+3]/255;if(a<0.1)continue;total+=(data[i]*.2126+data[i+1]*.7152+data[i+2]*.0722)*a;weight+=a;}
 const mean=Math.max(24,total/Math.max(1,weight));
 for(let i=0;i<data.length;i+=4){if(!data[i+3])continue;
  const lum=data[i]*.2126+data[i+1]*.7152+data[i+2]*.0722;
  const factor=Math.max(.18,Math.min(1.75,lum/mean));
  for(let channel=0;channel<3;channel++)data[i+channel]=Math.min(255,target[channel]*factor);
 }
}
type Raster=HTMLImageElement|HTMLCanvasElement;
const cache=new WeakMap<Raster,Map<string,HTMLCanvasElement>>();
export function styledGarment(image:Raster,style?:GarmentStyle,texture?:Raster):Raster {
 if(!style?.color && !texture)return image;
 const key=JSON.stringify([style?.color,style?.pattern,!!texture]);
 const variants=cache.get(image)??new Map<string,HTMLCanvasElement>();
 const cached=variants.get(key);if(cached)return cached;
 const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=1536;
 const context=canvas.getContext('2d');if(!context)return image;
 context.drawImage(image,0,0,1024,1536);
 const pixels=context.getImageData(0,0,1024,1536);
 if(style?.color)colorizePixels(pixels.data,style.color);
 if(texture){
  const tile=document.createElement('canvas');tile.width=tile.height=style?.pattern==='ke-soc'||style?.pattern==='cham-bi'?160:300;
  const tc=tile.getContext('2d');const overlay=document.createElement('canvas');overlay.width=1024;overlay.height=1536;
  const oc=overlay.getContext('2d');
  if(tc&&oc){tc.drawImage(texture,0,0,tile.width,tile.height);const fill=oc.createPattern(tile,'repeat');
   if(fill){oc.fillStyle=fill;oc.fillRect(0,0,1024,1536);const motif=oc.getImageData(0,0,1024,1536).data;
    for(let i=0;i<pixels.data.length;i+=4){if(!pixels.data[i+3])continue;
     const alpha=motif[i+3]/255*.78;
     const shade=.3+(pixels.data[i]*.2126+pixels.data[i+1]*.7152+pixels.data[i+2]*.0722)/255*.85;
     for(let c=0;c<3;c++)pixels.data[i+c]=pixels.data[i+c]*(1-alpha)+motif[i+c]*shade*alpha;
    }
   }
  }
 }
 context.putImageData(pixels,0,0);if(variants.size>=4)variants.delete(variants.keys().next().value!);
 variants.set(key,canvas);cache.set(image,variants);return canvas;
}
