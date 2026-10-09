import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {withHandForeground} from '../frontend/src/utils/sourceDirectionRenderer.ts';
import {renderMaleCharacter,characterHeadroom} from '../frontend/src/utils/renderMaleCharacter.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url)),{createCanvas,loadImage,GlobalFonts}=require('@napi-rs/canvas');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arial.ttf','Asset Preview');
globalThis.document={createElement:()=>createCanvas(1,1)};
const views=['front','left','right','back'],height=1536+characterHeadroom;
for(const gender of ['male','female']){
 globalThis.gc?.();
 const publicRoot=path.join(root,`frontend/public/figure/${gender}-layers`),catalog=JSON.parse(await readFile(path.join(publicRoot,'catalog.json'),'utf8')),images={};
 const items=[...catalog.shoes,...catalog.accessories];
 const files=new Set([...views.map(view=>`body/${view}.png`),...views.flatMap(view=>[`shirts/ba-ba/${view}.png`,`pants/ivory/${view}.png`])]);
 for(const file of files)images[file]=await loadImage(await readFile(path.join(publicRoot,file)));
 const fitted=withHandForeground(images,gender),newItems=items.filter(item=>item.sourcePrepared),sheet=createCanvas(1120,newItems.length*475),ctx=sheet.getContext('2d');ctx.fillStyle='#eee9dc';ctx.fillRect(0,0,sheet.width,sheet.height);
 for(const [row,item] of newItems.entries()){
  globalThis.gc?.();const rowImages={...fitted};
  for(const view of views){const file=item.file.replace('front.png',view+'.png');rowImages[file]=await loadImage(await readFile(path.join(publicRoot,file)));}
  for(const [column,view] of views.entries()){
  const canvas=createCanvas(1024,height),c=canvas.getContext('2d');
  const selection={shirt:'ba-ba',pants:'ivory',shoes:item.category==='shoes'?item.id:null,accessories:item.slot?{[item.slot]:item.id}:{}};
  renderMaleCharacter(c,rowImages,selection,gender,view);ctx.drawImage(canvas,column*280,row*475+20,280,455);ctx.fillStyle='#354830';ctx.font='12px "Asset Preview"';ctx.fillText(item.name+' / '+view,column*280+6,row*475+16);
  }
 }
 await mkdir(path.join(root,'assets/previews'),{recursive:true});await writeFile(path.join(root,`assets/previews/accessories-${gender}.png`),sheet.toBuffer('image/png'));
}
