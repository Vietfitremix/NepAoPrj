import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {readFile,writeFile,mkdir,copyFile,access} from 'node:fs/promises';
import {characterBaseFile,directionalGarmentFile} from '../frontend/src/utils/characterViews.ts';
import {withHandForeground} from '../frontend/src/utils/sourceDirectionRenderer.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),kit=path.join(root,'assets/exports/wardrobe/kit');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url)),{createCanvas,loadImage}=require('@napi-rs/canvas');
const views=['front','left','right','back'],manifest={width:1024,height:1736,layerHeight:1536,bodyOffsetY:200,views,items:[],patterns:[]},prompts=[];
globalThis.document={createElement:()=>createCanvas(1,1)};
for(const gender of ['male','female']){
 const publicRoot=path.join(root,`frontend/public/figure/${gender}-layers`),catalog=JSON.parse(await readFile(path.join(publicRoot,'catalog.json'),'utf8')),images={};
 for(const kind of ['base','prepared-base','shoe-base','prepared-shoe-base','hands'])await mkdir(path.join(kit,`characters/${gender}/${kind}`),{recursive:true});
 for(const view of views){const file=characterBaseFile(gender,view);images[file]=await loadImage(await readFile(path.join(publicRoot,file)));await copyFile(path.join(publicRoot,file),path.join(kit,`characters/${gender}/base/${view}.png`));}
 const prepared=withHandForeground(images,gender);
 for(const view of views){
  await writeFile(path.join(kit,`characters/${gender}/prepared-base/${view}.png`),prepared[`views/base-bottom-${view}.png`].toBuffer('image/png'));
  await writeFile(path.join(kit,`characters/${gender}/hands/${view}.png`),prepared[`views/hands-${view}.png`].toBuffer('image/png'));
  await writeFile(path.join(kit,`characters/${gender}/shoe-base/${view}.png`),prepared[`views/base-shoes-${view}.png`].toBuffer('image/png'));
  await writeFile(path.join(kit,`characters/${gender}/prepared-shoe-base/${view}.png`),prepared[`views/base-bottom-shoes-${view}.png`].toBuffer('image/png'));
 }
 for(const item of [...catalog.outfits,...catalog.pants,...catalog.shoes,...catalog.accessories]){
  const directory=`${gender}/${item.category}/${item.id}`,files={},source=path.dirname(path.join(root,item.reference));await mkdir(path.join(kit,directory),{recursive:true});
  for(const view of views){
   files[view]=`${directory}/${view}.png`;await copyFile(path.join(publicRoot,directionalGarmentFile(item.file,view)),path.join(kit,files[view]));
   const promptFile=path.join(source,`${view}.json`);
   try{await access(promptFile);}catch{continue;}
   prompts.push(JSON.parse(await readFile(promptFile,'utf8')));
  }
  await copyFile(path.join(publicRoot,item.thumbnail),path.join(kit,directory,'thumbnail.png'));
  manifest.items.push({gender,category:item.category,id:item.id,name:item.name,detail:item.detail,slot:item.slot,offsetY:item.offsetY??0,rearViews:item.rearViews,coversFeet:item.coversFeet,footbedClipY:item.footbedClipY,files,thumbnail:`${directory}/thumbnail.png`});
 }
}
const patterns=JSON.parse(await readFile(path.join(root,'frontend/public/figure/patterns/catalog.json'),'utf8'));
for(const item of patterns){await mkdir(path.join(kit,'patterns',item.id),{recursive:true});
 for(const name of ['tile','thumbnail'])await copyFile(path.join(root,`frontend/public/figure/patterns/${item.id}/${name}.png`),path.join(kit,`patterns/${item.id}/${name}.png`));
 manifest.patterns.push(item);prompts.push(JSON.parse(await readFile(path.join(root,`assets/patterns/${item.id}/source/tile.json`),'utf8')));
}
await writeFile(path.join(kit,'manifest.json'),JSON.stringify(manifest,null,2));await writeFile(path.join(kit,'prompts.json'),JSON.stringify(prompts,null,2));
await copyFile(path.join(root,'assets/README.md'),path.join(kit,'README.md'));
for(const name of ['bottoms-male','bottoms-female','traditional-male','traditional-female','accessories-male','accessories-female','patterns','styled-outfits'])await copyFile(path.join(root,`assets/previews/${name}.png`),path.join(kit,`preview-${name}.png`));
console.log(`Packaged ${manifest.items.length} categorized items / ${manifest.items.length*4} sprites / ${manifest.patterns.length} patterns.`);
