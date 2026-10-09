// One-time, lossless migration from flat asset folders to item categories.
import {readFile,writeFile,mkdir,rename,copyFile,access,readdir,rmdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),moves=[],spriteHashes=[];
const views=['front','left','right','back'];
const absolute=relative=>{const target=path.resolve(root,relative);if(!target.startsWith(root+path.sep))throw Error(`Outside workspace: ${target}`);return target;};
const exists=async relative=>{try{await access(absolute(relative));return true;}catch{return false;}};
async function move(from,to){if(!await exists(from))return; if(await exists(to))throw Error(`Destination already exists: ${to}`);await mkdir(path.dirname(absolute(to)),{recursive:true});await rename(absolute(from),absolute(to));moves.push({from,to});}
const catalogs={},bottoms=JSON.parse(await readFile(absolute('assets/bottoms-v2/items.json'),'utf8'));
for(const gender of ['male','female']){
 const publicRoot=`frontend/public/figure/${gender}-layers`,catalog=JSON.parse(await readFile(absolute(`${publicRoot}/catalog.json`),'utf8'));
 if(catalog.base==='body/front.png')throw Error('Asset folders are already organized.');
 catalogs[gender]=catalog;
 await move(`${publicRoot}/${gender==='male'?'base-barefoot.png':'base.png'}`,`${publicRoot}/body/front.png`);
 for(const view of views.slice(1))await move(`${publicRoot}/views/base-${view}.png`,`${publicRoot}/body/${view}.png`);
 await move(`${publicRoot}/base.prompt.txt`,`assets/wardrobe/${gender}/body/front.prompt.txt`);
 if(gender==='male')for(const file of ['base.png','female-base.png','female-base.prompt.txt'])await move(`${publicRoot}/${file}`,`assets/archive/body/${gender}/${file}`);
 catalog.base='body/front.png';
 for(const kind of ['outfits','pants','shoes'])for(const item of catalog[kind]){
  const oldFile=item.file,stem=oldFile.slice(0,-4),category=kind==='outfits'?'shirts':kind==='shoes'?'shoes':item.id.startsWith('skirt-')?'skirts':'pants';
  const directory=`${category}/${item.id}`,source=`assets/wardrobe/${gender}/${directory}/source`;
  for(const view of views){
   const from=`${publicRoot}/views/${stem}-${view}-source.png`,to=`${publicRoot}/${directory}/${view}.png`;
   const hash=createHash('sha256').update(await readFile(absolute(from))).digest('hex');
   await move(from,to);spriteHashes.push({file:to,hash});
  }
  await move(`${publicRoot}/${oldFile}`,`${source}/reference.png`);
  const thumbnail=`${publicRoot}/${directory}/thumbnail.png`;
  if(item.thumbnail)await move(`${publicRoot}/${item.thumbnail}`,thumbnail);
  else await copyFile(absolute(`${source}/reference.png`),absolute(thumbnail));
  await move(`${publicRoot}/${stem}.prompt.txt`,`${source}/reference.prompt.txt`);
  for(const view of views){
   const folder=item.sourcePrepared?'assets/bottoms-v2':'assets/source-layers';
   for(const ext of ['png','json'])await move(`${folder}/${gender}/${stem}-${view}.${ext}`,`${source}/${view}.${ext}`);
   await move(`${folder}/${gender}/${stem}-${view}-discarded.png`,`assets/archive/rejected/${gender}/${stem}-${view}.png`);
  }
  item.file=`${directory}/front.png`;item.thumbnail=`${directory}/thumbnail.png`;item.category=category;item.reference=`${source}/reference.png`;
  const bottom=bottoms.find(bottom=>bottom.gender===gender&&bottom.id===item.id);
  if(bottom){bottom.file=item.file;bottom.category=category;bottom.reference=item.reference;}
 }
 await move(`${publicRoot}/README.md`,`assets/archive/documentation/${gender}-layers-README.md`);
}
await mkdir(absolute('assets/metadata'),{recursive:true});
await writeFile(absolute('assets/metadata/bottoms-items.json'),JSON.stringify(bottoms,null,2)+'\n');
await move('assets/bottoms-v2/items.json','assets/archive/documentation/bottoms-items-original.json');
await move('assets/bottoms-v2/alignment.json','assets/metadata/bottoms-alignment.json');
await move('assets/source-layers/alignment.json','assets/metadata/traditional-alignment.json');
for(const gender of ['male','female'])await move(`assets/bottoms-v2/preview-${gender}.png`,`assets/previews/bottoms-${gender}.png`);
for(const view of views)await move(`assets/source-worn/male/ao-dai-navy-${view}-v1.png`,`assets/wardrobe/male/shirts/navy/validation/${view}.png`);
await move('assets/source-worn/prompts.json','assets/wardrobe/male/shirts/navy/validation/prompts.json');
await move('assets/source-worn/README.md','assets/wardrobe/male/shirts/navy/validation/README.md');
await move('assets/source-layers','assets/archive/packages/traditional');
await move('assets/bottoms-v2','assets/archive/packages/bottoms');
await move('assets/blender','assets/archive/blender');
const remap=value=>{
 if(typeof value==='string'){
  const normalized=value.replaceAll('\\','/'),relative=normalized.startsWith(root.replaceAll('\\','/')+'/')?normalized.slice(root.length+1):normalized;
  const match=moves.find(move=>move.from===relative);
  if(match)return normalized.startsWith(root.replaceAll('\\','/')+'/')?root.replaceAll('\\','/')+'/'+match.to:match.to;
  return value;
 }
 if(Array.isArray(value))return value.map(remap);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([key,value])=>[key,remap(value)]));
 return value;
};
async function updateJson(directory){for(const entry of await readdir(absolute(directory),{withFileTypes:true})){const file=`${directory}/${entry.name}`;if(entry.isDirectory())await updateJson(file);else if(entry.name.endsWith('.json')){const data=JSON.parse(await readFile(absolute(file),'utf8'));await writeFile(absolute(file),JSON.stringify(remap(data),null,2)+'\n');}}}
await updateJson('assets/wardrobe');await updateJson('assets/metadata');
for(const gender of ['male','female'])await writeFile(absolute(`frontend/public/figure/${gender}-layers/catalog.json`),JSON.stringify(catalogs[gender],null,2)+'\n');
async function removeEmpty(directory){if(!await exists(directory))return;for(const entry of await readdir(absolute(directory),{withFileTypes:true}))if(entry.isDirectory())await removeEmpty(`${directory}/${entry.name}`);if((await readdir(absolute(directory))).length===0)await rmdir(absolute(directory));}
for(const directory of ['assets/source-worn','frontend/public/figure/male-layers/views','frontend/public/figure/female-layers/views'])await removeEmpty(directory);
for(const sprite of spriteHashes)if(createHash('sha256').update(await readFile(absolute(sprite.file))).digest('hex')!==sprite.hash)throw Error(`Changed sprite: ${sprite.file}`);
await writeFile(absolute('assets/metadata/path-migration.json'),JSON.stringify({moves,spriteHashes},null,2)+'\n');
console.log(`Organized ${moves.length} paths. Verified ${spriteHashes.length} sprite files are unchanged.`);
