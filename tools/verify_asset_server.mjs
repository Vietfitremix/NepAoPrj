import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),origin='http://localhost:5173',urls=[];
for(const gender of ['male','female']){const prefix=`figure/${gender}-layers`,catalog=JSON.parse(await readFile(path.join(root,'frontend/public',prefix,'catalog.json'),'utf8'));
 for(const view of ['front','left','right','back'])urls.push(`${origin}/${prefix}/body/${view}.png`);
 for(const item of [...catalog.outfits,...catalog.pants,...catalog.shoes,...catalog.accessories]){
  for(const view of ['front','left','right','back'])urls.push(`${origin}/${prefix}/${item.file.replace('front.png',view+'.png')}`);
  urls.push(`${origin}/${prefix}/${item.thumbnail}`);
 }
}
const patterns=JSON.parse(await readFile(path.join(root,'frontend/public/figure/patterns/catalog.json'),'utf8'));
for(const item of patterns)urls.push(`${origin}/figure/${item.file}`,`${origin}/figure/${item.thumbnail}`);
for(let start=0;start<urls.length;start+=8)await Promise.all(urls.slice(start,start+8).map(async url=>{
 const response=await fetch(url,{method:'HEAD'});assert.equal(response.status,200,url);assert.match(response.headers.get('content-type')??'',/^image\/png/,url);
}));
console.log(`HTTP verified ${urls.length} categorized image URLs.`);
