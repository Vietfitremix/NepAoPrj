// Render the production accessory fitting path in batches for visual QA.
import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {withHandForeground} from '../frontend/src/utils/sourceDirectionRenderer.ts';
import {renderMaleCharacter} from '../frontend/src/utils/renderMaleCharacter.ts';
import {setWardrobeCatalogs} from '../frontend/src/utils/maleWardrobe.ts';
import {leftGarmentSourceFile} from '../frontend/src/utils/characterViews.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url));
const {createCanvas,loadImage}=require('@napi-rs/canvas');
globalThis.document={createElement:()=>createCanvas(1,1)};
const gender=process.argv[2]??'female',views=['front','left','right','back'];
const live=process.argv.includes('--live'),detail=process.argv.includes('--detail');
const origin='http://localhost:5173';
if(!['male','female'].includes(gender))throw Error('Expected male or female');
const directory=path.join(root,`frontend/public/figure/${gender}-layers`);
const catalogs=live?(await (await fetch(origin+'/api/data/bootstrap')).json()).wardrobes:undefined;
if(catalogs)setWardrobeCatalogs(catalogs);
const catalog=catalogs?.[gender]??JSON.parse(await readFile(path.join(directory,'catalog.json'),'utf8')),images={};
const itemFilter=process.argv.find(arg=>arg.startsWith('--item='))?.slice(7);
const accessoryItems=itemFilter?catalog.accessories.filter(item=>item.id===itemFilter):catalog.accessories;
async function asset(file){
  if(!live)return loadImage(await readFile(path.join(directory,file)));
  const response=await fetch(file.startsWith('/api/')?origin+file:origin+`/figure/${gender}-layers/`+file);
  if(!response.ok)throw Error('Asset HTTP '+response.status+': '+file);
  return loadImage(Buffer.from(await response.arrayBuffer()));
}
function drawFigure(ctx,figure,item,column,row){
  const profile=column===1||column===2;
  const roi=!detail?[0,0,1024,1736]:['headwear','headphones','glasses','hairAccessory','earrings','necklace'].includes(item.slot)
    ?[280,60,460,540]:['gloves','bracelet'].includes(item.slot)
    ?profile?[360,880,290,330]:[170,885,680,280]:[180,450,660,950];
  ctx.drawImage(figure,...roi,column*260,row*450+16,260,Math.min(434,roi[3]*260/roi[2]));
}
const prefix=`assets/previews/accessory-fit-${live?'live-':''}${gender}${detail?'-detail':''}${itemFilter?'-'+itemFilter:''}`;
for(const view of views)for(const file of [`body/${view}.png`,`shirts/ba-ba/${view}.png`,`pants/ivory/${view}.png`])
  images[file]=await asset(file);
if(live){const shirt=catalog.outfits.find(item=>item.id==='ba-ba'),file=leftGarmentSourceFile(shirt.reference);images[file]=await asset(file);}
const base=withHandForeground(images,gender);
await mkdir(path.join(root,'assets/previews'),{recursive:true});
for(let batch=0;batch<Math.ceil(accessoryItems.length/6);batch++){
  const items=accessoryItems.slice(batch*6,batch*6+6),sheet=createCanvas(1040,items.length*450),ctx=sheet.getContext('2d');
  ctx.fillStyle='#eee9dc';ctx.fillRect(0,0,sheet.width,sheet.height);
  for(const [row,item] of items.entries()){
    const layers={...base};
    for(const view of views){const file=item.file.replace('front.png',view+'.png');layers[file]=await asset(file);}
    for(const [column,view] of views.entries()){
      const figure=createCanvas(1024,1736);
      renderMaleCharacter(figure.getContext('2d'),layers,{shirt:'ba-ba',pants:'ivory',shoes:null,accessories:{[item.slot]:item.id}},gender,view);
      drawFigure(ctx,figure,item,column,row);
      ctx.fillStyle='#354830';ctx.font='12px Arial';ctx.fillText(item.id+' / '+view,column*260+6,row*450+13);
    }
  }
  const output=`${prefix}-${batch+1}.png`;
  await writeFile(path.join(root,output),sheet.toBuffer('image/png'));
  console.log(output);
}
if(itemFilter)process.exit(0);
const carriers=['tui-coi','tui-tote','tui-deo-cheo','ba-lo'];
const sheet=createCanvas(1040,carriers.length*450),ctx=sheet.getContext('2d');
ctx.fillStyle='#eee9dc';ctx.fillRect(0,0,sheet.width,sheet.height);
const charm=catalog.accessories.find(item=>item.slot==='bagCharm');
for(const [row,id] of carriers.entries()){
  const item=catalog.accessories.find(item=>item.id===id),layers={...base};
  for(const source of [item,charm])for(const view of views){
    const file=source.file.replace('front.png',view+'.png');layers[file]=await asset(file);
  }
  for(const [column,view] of views.entries()){
    const figure=createCanvas(1024,1736);
    renderMaleCharacter(figure.getContext('2d'),layers,{shirt:'ba-ba',pants:'ivory',shoes:null,
      accessories:{[item.slot]:id,bagCharm:charm.id}},gender,view);
    ctx.drawImage(figure,column*260,row*450+16,260,434);
    ctx.fillStyle='#354830';ctx.font='12px Arial';ctx.fillText(id+' + charm / '+view,column*260+6,row*450+13);
  }
}
const output=`${prefix}-carriers.png`;
await writeFile(path.join(root,output),sheet.toBuffer('image/png'));console.log(output);
