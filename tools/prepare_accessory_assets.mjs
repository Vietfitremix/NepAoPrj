// Split generated turnarounds, preserve alpha, and fit each item to both avatars.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,copyFile,access} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {handRegions} from '../frontend/src/utils/sourceDirectionRenderer.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url));
const {createCanvas,loadImage}=require('@napi-rs/canvas');
const views=['front','left','right','back'],items=JSON.parse(await readFile(path.join(root,'assets/metadata/accessory-items.json'),'utf8')),records=[];
const partial=process.argv.includes('--partial');
function box(canvas,x0=0,x1=canvas.width,y0=0,y1=canvas.height){const data=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;let l=canvas.width,t=canvas.height,r=-1,b=-1;
 for(let y=Math.floor(y0);y<Math.ceil(y1);y++)for(let x=x0;x<x1;x++)if(data[(y*canvas.width+x)*4+3]>100){l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);}
 if(r<l)throw Error('Empty source cell');return{x:Math.max(x0,l-3),y:Math.max(0,t-3),w:Math.min(x1,r+4)-Math.max(x0,l-3),h:Math.min(canvas.height,b+4)-Math.max(0,t-3)};}
function draw(ctx,source,crop,target){ctx.drawImage(source,crop.x,crop.y,crop.w,crop.h,...target);}
const bodies=new Map();
async function fitGloveMask(ctx,gender,view){
 const key=gender+'/'+view;if(!bodies.has(key))bodies.set(key,await loadImage(await readFile(path.join(root,`frontend/public/figure/${gender}-layers/body/${view}.png`))));
 const mask=createCanvas(1024,1536),mc=mask.getContext('2d'),regions=[...handRegions[gender][view]];
 if(view==='back')regions.push(regions[0].map(([x,y])=>[1024-x,y]));
 mc.beginPath();for(const region of regions){region.forEach(([x,y],i)=>i?mc.lineTo(x,y):mc.moveTo(x,y));mc.closePath();}mc.clip();mc.drawImage(bodies.get(key),0,0);
 const skin=mc.getImageData(0,0,1024,1536).data,pixels=ctx.getImageData(0,0,1024,1536);
 for(let y=690;y<890;y++)for(let x=180;x<845;x++){
  const index=(y*1024+x)*4;if(!pixels.data[index+3])continue;let found=false;
  for(let dy=-2;dy<=2&&!found;dy++)for(let dx=-2;dx<=2;dx++){const i=((y+dy)*1024+x+dx)*4;if(skin[i+3]>180&&skin[i]>skin[i+1]*1.06&&skin[i+1]>skin[i+2]*1.06){found=true;break;}}
  if(!found)pixels.data[index+3]=0;
 }
 ctx.putImageData(pixels,0,0);
}
function targets(item,gender,view,source,bounds){const male=gender==='male',profile=view==='left'||view==='right';
 if(item.slot==='headwear'){
  const center=profile?(view==='left'?520:506):512;
  if(item.id==='mu-luoi-trai'){const width=profile?240:215;return[{crop:bounds,target:[center-width/2,200+(male?-30:-16),width,140]}];}
  if(item.id==='mu-cao-boi'){const width=male?350:335,height=bounds.h*width/bounds.w;return[{crop:bounds,target:[center-width/2,200+105-height*.87,width,height]}];}
  if(item.id==='non-la'||item.id==='non-quai-thao'){
   const width=item.id==='non-la'?(male?430:400):(male?560:530),height=bounds.h*width/bounds.w;
   const brim=male?110:115,ratio=item.id==='non-la'?.63:.15;
   return [{crop:bounds,target:[center-width/2,200+brim-height*ratio,width,height]}];
  }
  const width=item.id==='khan-mo-qua'?(male?245:240):(male?205:200),height=item.id==='khan-mo-qua'?280:item.id==='khan-xep'?135:95;
  return [{crop:bounds,target:[center-width/2,200+(male?4:18),width,height]}];
 }
 if(item.slot==='headphones'){
  const cut=bounds.y+bounds.h*.48,band=box(source,0,source.width,0,cut);
  if(profile){const center=view==='left'?(male?526:522):(male?500:486),pad=box(source,0,source.width,cut,source.height);
   return[{crop:band,target:[center-20,male?18:32,40,115]},{crop:pad,target:[center-40,male?116:128,80,84]}];
  }
  const left=box(source,0,Math.floor(source.width/2),cut,source.height),right=box(source,Math.floor(source.width/2),source.width,cut,source.height);
  return[{crop:band,target:[408,male?12:25,208,117]},{crop:left,target:[male?400:404,male?116:128,51,81]},{crop:right,target:[574,male?116:128,51,81]}];
 }
 if(item.slot==='glasses')return[{crop:bounds,target:[profile?(view==='left'?(male?437:430):(male?464:470)):449,male?114:126,profile?115:130,40]}];
 if(item.slot==='bagCharm')return[{crop:bounds,target:[view==='front'?male?653:623:view==='back'?male?305:335:view==='right'?537:432,680,60,90]}];
 if(item.slot==='hipChain')return[{crop:bounds,target:[view==='front'?male?572:558:view==='back'?male?332:368:view==='right'?440:433,650,profile?125:male?118:100,110]}];
 if(item.slot==='backpack'){
  const target=view==='front'?[male?366:385,275,male?292:255,445]:view==='back'?[male?350:374,290,male?324:278,460]:view==='left'?[430,275,330,500]:[266,275,335,500];
  return[{crop:bounds,target}];
 }
 if(item.slot==='gloves'){
  if(profile)return[{crop:bounds,target:[view==='right'?male?489:499:male?436:440,male?728:727,male?95:79,96]}];
  const left=box(source,0,Math.floor(source.width/2)),right=box(source,Math.floor(source.width/2),source.width),front=view==='front';
  const positions=male?(front?[204,747]:[205,742]):(front?[251,698]:[240,700]);
  return[{crop:left,target:[positions[0],male?732:726,male?76:71,92]},{crop:right,target:[positions[1],male?732:726,male?76:71,92]}];
 }
 if(item.slot==='hairAccessory'){
  const x=view==='front'?583:view==='back'?397:view==='right'?435:570;
  return [{crop:bounds,target:[x,male?82:95,49,49]}];
 }
 if(item.slot==='shoes'){
  if(profile)return[{crop:bounds,target:[view==='right'?male?432:422:male?345:355,1325,view==='left'?(male?250:245):(male?226:213),119]}];
  const left=box(source,0,Math.floor(source.width/2)),right=box(source,Math.floor(source.width/2),source.width);
  const positions=male?(view==='front'?[302,585]:[302,595]):(view==='front'?[363,569]:[365,565]);
  return [{crop:left,target:[positions[0],view==='front'?1320:1310,male?145:115,120]}, {crop:right,target:[positions[1],view==='front'?1320:1310,male?145:115,120]}];
 }
 if(item.slot==='bag'){
  if(item.id==='tui-deo-cheo')return[{crop:bounds,target:view==='front'?[male?328:360,275,male?395:355,515]:view==='back'?[male?300:330,275,male?395:355,515]:view==='left'?[408,275,205,515]:[410,275,205,515]}];
  const width=profile?62:170,height=215,x=view==='front'?(male?697:657):view==='back'?(male?169:200):view==='right'?518:448;
  return[{crop:bounds,target:[x,male?810:810,width,height]}];
 }
 if(item.slot==='fan'){
  const width=profile?26:210,x=view==='front'?(male?130:175):view==='back'?(male?677:637):view==='left'?459:536;
  return[{crop:bounds,target:[x,male?812:821,width,230]}];
 }
 if(item.slot==='necklace')return[{crop:bounds,target:profile?[view==='right'?510:444,252,45,76]:[male?431:435,view==='back'?242:254,male?162:154,64]}];
 if(item.slot==='earrings'){
  if(profile)return[{crop:bounds,target:[view==='right'?(male?497:483):(male?519:516),male?179:190,16,32]}];
  const left=box(source,0,Math.floor(source.width/2)),right=box(source,Math.floor(source.width/2),source.width);
  return[{crop:left,target:[male?435:435,male?170:179,16,32]},{crop:right,target:[male?570:575,male?170:179,16,32]}];
 }
 if(item.slot==='bracelet')return[{crop:bounds,target:[view==='front'?(male?757:718):view==='back'?(male?221:253):view==='right'?(male?501:502):455,male?733:727,male?54:43,19]}];
 throw Error('Unknown slot '+item.slot);
}
for(const item of items){let metadata;
 try{metadata=JSON.parse(await readFile(path.join(root,`assets/metadata/accessory-sources/${item.id}.json`),'utf8'));}catch(error){if(partial&&error.code==='ENOENT')continue;throw error;}
 const sourceRoot=`assets/wardrobe/shared/${item.category}/${item.id}/source`;await mkdir(path.join(root,sourceRoot),{recursive:true});
 await copyFile(metadata.generatedPath,path.join(root,sourceRoot,'turnaround.png'));
 await writeFile(path.join(root,sourceRoot,'turnaround.json'),JSON.stringify({...metadata,file:`${sourceRoot}/turnaround.png`},null,2));
 const sheet=await loadImage(await readFile(path.join(root,sourceRoot,'turnaround.png'))),cells={};
 for(const [index,view] of views.entries()){
  const canvas=createCanvas(Math.floor(sheet.width/2),Math.floor(sheet.height/2)),ctx=canvas.getContext('2d');
  ctx.drawImage(sheet,index%2*sheet.width/2,Math.floor(index/2)*sheet.height/2,sheet.width/2,sheet.height/2,0,0,canvas.width,canvas.height);cells[view]=canvas;
 }
 for(const gender of ['male','female']){
  const publicRoot=`frontend/public/figure/${gender}-layers`,directory=`${item.category}/${item.id}`,rawRoot=`assets/wardrobe/${gender}/${directory}/source`;
  await mkdir(path.join(root,publicRoot,directory),{recursive:true});await mkdir(path.join(root,rawRoot),{recursive:true});
  for(const view of views){const source=cells[view],bounds=box(source),placements=targets(item,gender,view,source,bounds),canvas=createCanvas(1024,1536),ctx=canvas.getContext('2d');
   for(const placement of placements)draw(ctx,source,placement.crop,placement.target);
   if(item.slot==='gloves')await fitGloveMask(ctx,gender,view);
   await writeFile(path.join(root,publicRoot,directory,view+'.png'),canvas.toBuffer('image/png'));
   await writeFile(path.join(root,rawRoot,view+'.png'),source.toBuffer('image/png'));
   const meta={tool:'image_gen',file:`${rawRoot}/${view}.png`,view,prompt:metadata.prompt,inputs:[`${sourceRoot}/turnaround.png`,`frontend/public/figure/${gender}-layers/body/${view}.png`],generatedPath:metadata.generatedPath};
   await writeFile(path.join(root,rawRoot,view+'.json'),JSON.stringify(meta,null,2));
   if(view==='front'){await writeFile(path.join(root,rawRoot,'reference.png'),source.toBuffer('image/png'));
    const thumbnail=createCanvas(512,512),tc=thumbnail.getContext('2d'),scale=Math.min(460/bounds.w,460/bounds.h);
    tc.drawImage(source,bounds.x,bounds.y,bounds.w,bounds.h,(512-bounds.w*scale)/2,(512-bounds.h*scale)/2,bounds.w*scale,bounds.h*scale);
    await writeFile(path.join(root,publicRoot,directory,'thumbnail.png'),thumbnail.toBuffer('image/png'));
   }
   records.push({gender,id:item.id,view,file:`${directory}/${view}.png`,offsetY:item.slot==='headwear'?-200:0,placements});
  }
 }
}
await writeFile(path.join(root,'assets/metadata/accessory-alignment.json'),JSON.stringify(records,null,2));
if(process.argv.includes('--register')){
 if(records.length!==items.length*8)throw Error('All accessory source views must be ready before registering');
 for(const gender of ['male','female']){const catalogFile=path.join(root,`frontend/public/figure/${gender}-layers/catalog.json`),catalog=JSON.parse(await readFile(catalogFile,'utf8'));catalog.accessories??=[];
  for(const item of items){const directory=`${item.category}/${item.id}`,entry={id:item.id,name:item.name,detail:item.detail,category:item.category,file:`${directory}/front.png`,thumbnail:`${directory}/thumbnail.png`,reference:`assets/wardrobe/${gender}/${directory}/source/reference.png`,sourcePrepared:true,x:0,y:0,sx:1,sy:1,...(item.slot==='shoes'?{crops:[],coversFeet:!['guoc','dep-crocs','dep-le'].includes(item.id)}:{slot:item.slot,offsetY:item.slot==='headwear'?-200:0,rearViews:item.slot==='backpack'?['left','right']:item.slot==='glasses'?['back']:item.id==='tui-deo-cheo'?['left']:['bag','bracelet','hairAccessory'].includes(item.slot)?['left']:item.slot==='fan'?['right']:[]})};
   if(['dep-crocs','dep-le'].includes(item.id))entry.footbedClipY=1400;
   const group=item.slot==='shoes'?catalog.shoes:catalog.accessories,index=group.findIndex(other=>other.id===item.id);if(index<0)group.push(entry);else group[index]=entry;
  }
  await writeFile(catalogFile,JSON.stringify(catalog,null,2)+'\n');
 }
}
console.log(`Prepared ${records.length}/${items.length*8} accessory sprites.`);
