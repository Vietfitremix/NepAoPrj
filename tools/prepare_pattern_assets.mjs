import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(new URL('../.tools/asset-qa/package.json',import.meta.url)),{createCanvas,loadImage,GlobalFonts}=require('@napi-rs/canvas');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arial.ttf','Asset Preview');
const catalog=JSON.parse(await readFile(path.join(root,'frontend/public/figure/patterns/catalog.json'),'utf8'));
for(const item of catalog){
 const metadata=JSON.parse(await readFile(path.join(root,`assets/metadata/pattern-sources/${item.id}.json`),'utf8'));
 const sourceRoot=`assets/patterns/${item.id}/source`,publicRoot=`frontend/public/figure/patterns/${item.id}`;
 await mkdir(path.join(root,sourceRoot),{recursive:true});await mkdir(path.join(root,publicRoot),{recursive:true});
 await copyFile(metadata.generatedPath,path.join(root,sourceRoot,'tile.png'));
 await writeFile(path.join(root,sourceRoot,'tile.json'),JSON.stringify({...metadata,file:`${sourceRoot}/tile.png`,inputs:[]},null,2));
 const image=await loadImage(await readFile(path.join(root,sourceRoot,'tile.png')));
 for(const [file,size] of [['tile.png',1024],['thumbnail.png',256]]){const canvas=createCanvas(size,size);canvas.getContext('2d').drawImage(image,0,0,size,size);await writeFile(path.join(root,publicRoot,file),canvas.toBuffer('image/png'));}
}
await mkdir(path.join(root,'assets/previews'),{recursive:true});
const sheet=createCanvas(1200,Math.ceil(catalog.length/6)*240),ctx=sheet.getContext('2d');ctx.fillStyle='#dedbd0';ctx.fillRect(0,0,sheet.width,sheet.height);
for(const [i,item] of catalog.entries()){const image=await loadImage(await readFile(path.join(root,'frontend/public/figure',item.thumbnail)));ctx.drawImage(image,i%6*200,Math.floor(i/6)*240,200,200);ctx.fillStyle='#354830';ctx.font='13px "Asset Preview"';ctx.fillText(item.name,i%6*200+8,Math.floor(i/6)*240+224);}
await writeFile(path.join(root,'assets/previews/patterns.png'),sheet.toBuffer('image/png'));
console.log(`Prepared ${catalog.length} transparent pattern tiles and thumbnails.`);
