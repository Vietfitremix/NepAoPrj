import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {characterBaseFile,directionalGarmentFile} from '../frontend/src/utils/characterViews.ts';
import {withHandForeground} from '../frontend/src/utils/sourceDirectionRenderer.ts';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),output=path.join(root,'assets/exports/bottoms'),kit=path.join(output,'kit');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url));
const {createCanvas,loadImage}=require('@napi-rs/canvas');
const items=JSON.parse(await readFile(path.join(root,'assets/metadata/bottoms-items.json'),'utf8')),views=['front','left','right','back'],manifest={width:1024,height:1536,views,items:[]},prompts=[];
globalThis.document={createElement:()=>createCanvas(1024,1536)};
for(const gender of ['male','female']){
 const source=path.join(root,`frontend/public/figure/${gender}-layers`),images={};
 for(const kind of ['base','prepared-base','hands'])await mkdir(path.join(kit,`characters/${gender}/${kind}`),{recursive:true});
 for(const view of views){const file=characterBaseFile(gender,view);images[file]=await loadImage(await readFile(path.join(source,file)));await copyFile(path.join(source,file),path.join(kit,`characters/${gender}/base/${view}.png`));}
 const prepared=withHandForeground(images,gender);
 for(const view of views){
  await writeFile(path.join(kit,`characters/${gender}/prepared-base/${view}.png`),prepared[`views/base-bottom-${view}.png`].toBuffer('image/png'));
  await writeFile(path.join(kit,`characters/${gender}/hands/${view}.png`),prepared[`views/hands-${view}.png`].toBuffer('image/png'));
 }
 for(const item of items.filter(item=>item.gender===gender)){
  const directory=`${gender}/${item.category}/${item.id}`,files={};await mkdir(path.join(kit,directory),{recursive:true});
  for(const view of views){
   files[view]=`${directory}/${view}.png`;const src=path.join(source,directionalGarmentFile(item.file,view));
   const png=await readFile(src);if(png.readUInt32BE(16)!==1024||png.readUInt32BE(20)!==1536||png[25]!==6)throw Error(`Invalid RGBA sprite: ${src}`);
   await copyFile(src,path.join(kit,files[view]));
   prompts.push(JSON.parse(await readFile(path.join(root,`assets/wardrobe/${gender}/${item.category}/${item.id}/source/${view}.json`),'utf8')));
  }
  manifest.items.push({gender,id:item.id,name:item.name,detail:item.detail,files});
 }
 await copyFile(path.join(root,`assets/previews/bottoms-${gender}.png`),path.join(kit,`preview-${gender}.png`));
}
await copyFile(path.join(root,'assets/README.md'),path.join(kit,'README.md'));
await copyFile(path.join(root,'assets/metadata/bottoms-items.json'),path.join(kit,'items.json'));
await copyFile(path.join(root,'assets/metadata/bottoms-alignment.json'),path.join(kit,'alignment.json'));
await writeFile(path.join(kit,'manifest.json'),JSON.stringify(manifest,null,2));await writeFile(path.join(kit,'prompts.json'),JSON.stringify(prompts,null,2));
console.log(`Kit contains ${manifest.items.length} items, ${prompts.length} transparent sprites and their prompts.`);
